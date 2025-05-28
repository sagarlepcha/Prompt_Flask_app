
import app

def test_home():
    client = app.app.test_client()  # assuming your Flask app = Flask(__name__)
    response = client.get('/')
    assert response.status_code == 200