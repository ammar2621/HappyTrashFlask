from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from apps.users.model import Users
from passlib.hash import sha256_crypt

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResources(Resource):
    """Class for storing HTTP request method for create token and get claim information"""

    def options(self):
        """Init function needed to indicate this is a class, but never used"""
        return {'Status': 'OK'}, 200

    def post(self):
        """Post data from user to create token

        Retrieve data from user input located in JSON, validate the data, then create token.

        Args (located in JSON):
            email: A string of user's email
            password: A string of user's password

        Returns:
            A dict mapping keys to the corresponding value, for example:

            {
                "status": "ok",
                "email": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            }
        
        Raises: 
            Bad Request (400): An error that occured when some of the field is missing, or if the data is not valid (email and mobile phone inputted is wrong formatted)
            Unauthorized (401): A 401 error response indicates that the client tried to operate on a protected resource without providing the proper authorization. It may have provided the wrong credentials or none at all.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, location='json', required=True)
        parser.add_argument('password', type=str, location='json', required= True)
        args = parser.parse_args()

        # We use isEmailAddressValid function to check whether email inputted is valid or not

        if not Users.isEmailAddressValid(args['email']):
            return { 'message': 'Invalid email format!'}, 400, {'Content-Type': 'application/json'}

        
        # Check whether email is exist in database

        user = Users.query.filter_by(email=args['email']).first()
        if user is None:
            return {'status': 'UNATHORIZED', 'message': 'invalid email or password'}, 401, {'Content-Type': 'application/json'}


        # Check whether password is valid

        user_data = marshal(user, Users.login_response_field)
        if not sha256_crypt.verify(args['password'], user_data['password']):
            return {'status': 'UNATHORIZED', 'message': 'invalid email or password'}, 401, {'Content-Type': 'application/json'}

        
        # Create token

        user_data.pop('password') # Put password information out from user_claim
        token = create_access_token(identity=args['email'], user_claims=user_data)

        return {'status': 'ok',  'token': token}, 200

#     ## Function for get user information based on token
#     @jwt_required
#     def get(self):
#         claims = get_jwt_claims()
#         return {'claims': claims}, 200

# class RefreshTokenResources(Resource):

#     ## Options function needed to make interaction between react and api successfull
#     def options(self):
#         return {'Status': 'OK'}, 200
    
#     ## Function for get newer token before previous token expired
#     @jwt_required
#     def post(self):
#         current_user = get_jwt_identity()
#         current_claim = get_jwt_claims()
#         token = create_access_token(identity=current_user, user_claims=current_claim)
#         return {'token': token}, 200
        

api.add_resource(CreateTokenResources, '')
# api.add_resource(RefreshTokenResources, '/refresh')
