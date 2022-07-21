import pytest
import os
import tempfile
from app import app

@pytest.fixture
def client():
    app.config.update({'TESTING': True})

    with app.test_client() as client:
        yield client
class TestCurrencyConvertorClass:

    @pytest.fixture(autouse=True)
    def test_signup(self):
      resp = client.get('/handle-signup')
      assert b'Sign up' in resp.data 

    def test_signin(self):
      resp = client.get('/handle-signin')
      assert b'Sign in' in resp.data  
    def test_update_profile(self):
      resp = client.get('/handle-update-profile')
      assert b'profile-update' in resp.data  
    def test_transfer_money(self):
      resp = client.get('/handle-update-profile')
      assert b'transfer money' in resp.data     