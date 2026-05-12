from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
import boto3, os, time
from flask_cors import CORS

# Prometheus monitoring
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry

# Metrics
REQUEST_COUNT = Counter(
    'cloudgallery_request_count', 'Total HTTP requests', ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'cloudgallery_request_latency_seconds', 'Request latency', ['endpoint']
)

app = Flask(__name__)
CORS(app)

# Use AWS credentials from environment or ~/.aws/credentials or IAM role
S3_BUCKET = os.environ.get("CLOUDGALLERY_BUCKET", "cloudgallery-storage")
S3_REGION = os.environ.get("CLOUDGALLERY_REGION", "us-east-1")
# If PRESIGNED=1, return presigned URLs instead of public URLs
USE_PRESIGNED = os.environ.get("CLOUDGALLERY_PRESIGNED", "0") in ("1", "true", "True")

s3 = boto3.client('s3', region_name=S3_REGION)


# Simple request timing and metrics collection
@app.before_request
def start_timer():
    request._start_time = time.time()


@app.after_request
def record_metrics(response):
    try:
        endpoint = request.path
        method = request.method
        status = response.status_code
        elapsed = time.time() - getattr(request, '_start_time', time.time())
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
    except Exception:
        # don't let metrics collection break the app
        pass
    return response


@app.route('/metrics', methods=['GET'])
def metrics():
    # Expose Prometheus metrics
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files or 'album' not in request.form:
        return jsonify({"error": "Missing image or album"}), 400

    file = request.files['image']
    album = request.form['album'].strip() or "default"
    filename = secure_filename(file.filename)
    # prefix with timestamp to avoid accidental collisions
    key = f"{album}/{int(time.time())}-{filename}"

    # Only set ACL if not using presigned mode (for buckets that allow ACLs)
    extra = {}
    if not USE_PRESIGNED:
        extra['ACL'] = 'public-read'
    try:
        if extra:
            s3.upload_fileobj(file, S3_BUCKET, key, ExtraArgs=extra)
        else:
            s3.upload_fileobj(file, S3_BUCKET, key)
    except Exception as e:
        return jsonify({"error": "Upload failed", "details": str(e)}), 500

    if USE_PRESIGNED:
        url = s3.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': key}, ExpiresIn=3600)
    else:
        url = f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"

    return jsonify({"message": "Upload successful", "url": url})


@app.route('/albums', methods=['GET'])
def get_albums():
    # list objects and group by album prefix
    try:
        resp = s3.list_objects_v2(Bucket=S3_BUCKET)
    except Exception as e:
        return jsonify({"error": "Failed to list bucket", "details": str(e)}), 500

    contents = resp.get('Contents', [])
    albums = {}
    for obj in contents:
        # skip malformed keys
        if '/' not in obj['Key']:
            continue
        album, _ = obj['Key'].split('/', 1)
        if USE_PRESIGNED:
            url = s3.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': obj['Key']}, ExpiresIn=3600)
        else:
            url = f"https://{S3_BUCKET}.s3.amazonaws.com/{obj['Key']}"
        # return both the object key and the (possibly presigned) url
        albums.setdefault(album, []).append({"key": obj['Key'], "url": url})
       
    return jsonify(albums)


@app.route('/image/<path:key>', methods=['GET'])
def proxy_image(key):
    # Proxy an S3 object through the backend. This is useful when objects are private
    # and the frontend cannot directly load them (or to avoid CORS issues). The backend
    # must have permission to s3:GetObject for this bucket.
    try:
        resp = s3.get_object(Bucket=S3_BUCKET, Key=key)
    except Exception as e:
        return jsonify({"error": "Failed to get object", "details": str(e)}), 500

    data = resp['Body'].read()
    content_type = resp.get('ContentType', 'application/octet-stream')
    return Response(data, mimetype=content_type)


@app.route('/debug_objects', methods=['GET'])
def debug_objects():
    # Development-only: list raw S3 keys when CLOUDGALLERY_DEBUG is enabled
    if os.environ.get('CLOUDGALLERY_DEBUG', '0') not in ('1', 'true', 'True'):
        return jsonify({"error": "debug disabled"}), 403
    try:
        resp = s3.list_objects_v2(Bucket=S3_BUCKET)
    except Exception as e:
        return jsonify({"error": "Failed to list bucket", "details": str(e)}), 500
    contents = resp.get('Contents', [])
    keys = [obj['Key'] for obj in contents]
    return jsonify({"keys": keys})


@app.route('/api-ui', methods=['GET'])
def api_ui():
        # Small single-file UI to interact with the API (helpful for debugging)
        html = '''
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>CloudGallery API UI</title>
            <style>body{font-family:Arial,Helvetica,sans-serif;padding:20px}textarea{width:100%;height:200px}</style>
        </head>
        <body>
            <h1>CloudGallery API UI</h1>
            <p>
                <button onclick="checkHealth()">Check /health</button>
                <button onclick="listAlbums()">List /albums</button>
                <button onclick="listDebug()">List /debug_objects</button>
            </p>

            <h2>Upload image</h2>
            <form id="uploadForm" onsubmit="uploadImage(event)">
                Album: <input id="ui-album" name="album" value="default" />
                <input type="file" id="ui-image" name="image" />
                <button type="submit">Upload</button>
            </form>

            <h2>Output</h2>
            <div id="output"></div>

            <script>
                const API = '';
                async function checkHealth(){
                    const res = await fetch('/health');
                    document.getElementById('output').innerText = await res.text();
                }
                async function listAlbums(){
                    const res = await fetch('/albums');
                    const json = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(json, null, 2);
                }
                async function listDebug(){
                    const res = await fetch('/debug_objects');
                    const json = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(json, null, 2);
                }
                async function uploadImage(e){
                    e.preventDefault();
                    const fileEl = document.getElementById('ui-image');
                    if (!fileEl.files.length){ alert('Select a file'); return; }
                    const fd = new FormData();
                    fd.append('album', document.getElementById('ui-album').value || 'default');
                    fd.append('image', fileEl.files[0]);
                    const res = await fetch('/upload', {method: 'POST', body: fd});
                            // Try to parse JSON and show a short success message with link
                            try {
                                const data = await res.json();
                                const out = document.getElementById('output');
                                out.innerHTML = '';
                                if (res.ok) {
                                    const p = document.createElement('p');
                                    p.textContent = 'Successfully uploaded.';
                                    p.style.color = 'green';
                                    out.appendChild(p);
                                    if (data.url) {
                                        const a = document.createElement('a');
                                        a.href = data.url;
                                        a.target = '_blank';
                                        a.rel = 'noopener';
                                        a.textContent = 'View image';
                                        out.appendChild(a);
                                        const img = document.createElement('img');
                                        img.src = data.url;
                                        img.width = 150;
                                        img.style.display = 'block';
                                        img.style.marginTop = '8px';
                                        img.onerror = () => { img.style.display = 'none'; };
                                        out.appendChild(img);
                                    }
                                } else {
                                    const p = document.createElement('p');
                                    p.textContent = 'Upload failed: ' + (data.error || JSON.stringify(data));
                                    p.style.color = 'red';
                                    out.appendChild(p);
                                }
                            } catch (e) {
                                document.getElementById('output').innerText = await res.text();
                            }
                }
            </script>
        </body>
        </html>
        '''
        return html, 200, {'Content-Type': 'text/html'}


if __name__ == '__main__':
    # for local dev - use environment variable FLASK_DEBUG=1 for debug
    app.run(host='0.0.0.0', port=5005)
