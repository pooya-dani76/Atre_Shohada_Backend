from rest_framework_api_key.models import APIKey

def generate_test_api_key():
    api_key, key = APIKey.objects.create_key(name="test")
    return key



def init_test(self, login_required=False):
    key = generate_test_api_key()
    self.client.credentials(HTTP_X_API_KEY=key)    



