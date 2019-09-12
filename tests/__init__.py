import pytest, json, logging
from flask import Flask, request, json
from apps import app, db
from app import cache
import json
from apps.users.model import Users
from apps.trashes.model import ListTrash
from apps.trash_categories.model import ListTrashCategory
from passlib.hash import sha256_crypt

def call_client(request):
    client = app.test_client()
    return client

@pytest.fixture
def client(request):
    return call_client(request)

def resetDatabase():
    """Reset database for testing purpose"""
    db.drop_all()
    db.create_all()

    user_password_encrypted = sha256_crypt.hash('user')
    admin_password_encrypted = sha256_crypt.hash('admin')

    user = Users('user', 'user@user.com', '081122112211', user_password_encrypted, False)
    admin = Users('admin', 'admin@admin.com', '0811221122112', admin_password_encrypted, True)
    trash_category = ListTrashCategory('dummy_category')
    trash_one = {
        "trash_category_id" : 1,
        "trash_name" : "dummy_trash",
        "price" : 1000,
        "photo" : "dummy_photo",
        "point" : 1
    }
    trash_two = {
        "trash_category_id" : 1,
        "trash_name" : "dummy_trash",
        "price" : 2000,
        "photo" : "dummy_photo",
        "point" : 2
    }
    trash_instance_one = ListTrash(trash_one)
    trash_instance_two = ListTrash(trash_two)

    db.session.add(user)
    db.session.add(admin)
    db.session.add(trash_category)
    db.session.add(trash_instance_one)
    db.session.add(trash_instance_two)
    db.session.commit()


def createTokenUser():
    token = cache.get('token-user')
    if token is None:
        ## prepare request input
        data = {
            'email': 'user@user.com',
            'password': 'user'
        }

        ## do request
        req = call_client(request)
        res = req.post('/v1/auth',
                        data=json.dumps(data),
                        content_type='application/json')

        ## store response
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        ## assert / compare with expected result
        assert res.status_code == 200

        ## save token into cache
        cache.set('token-user', res_json['token'], timeout=60)

        ## return because it useful for other test
        return res_json['token']
    else:
        return token


def createTokenAdmin():
    token = cache.get('token-admin')
    if token is None:
        ## prepare request input
        data = {
            'email': 'admin@admin.com',
            'password': 'admin'
        }

        ## do request
        req = call_client(request)
        res = req.post('/v1/auth',
                        data=json.dumps(data),
                        content_type='application/json')

        ## store response
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        ## assert / compare with expected result
        assert res.status_code == 200

        ## save token into cache
        cache.set('token-admin', res_json['token'], timeout=60)

        ## return because it useful for other test
        return res_json['token']
    else:
        return token

def createTokenInvalid():
    token = cache.get('token-admin')
    if token is None:
        ## prepare request input
        data = {
            'email': 'admin@admin.com',
            'password': 'user'
        }

        ## do request
        req = call_client(request)
        res = req.post('/v1/auth',
                        data=json.dumps(data),
                        content_type='application/json') # seperti nembak API luar (contoh weather.io)

        ## store response
        res_json = json.loads(res.data)

        logging.warning('RESULT : %s', res_json)

        ## assert / compare with expected result
        assert res.status_code == 200

        ## save token into cache
        cache.set('token-admin', res_json['token'], timeout=60)

        ## return because it useful for other test
        return res_json['token']
    else:
        return token