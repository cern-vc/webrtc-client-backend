from flask import Blueprint
from flask_restful import Resource, Api

# class DocstringExampleClass(Resource):
#     """A bird with a flight speed exceeding that of an unladen swallow.
#
#     Attributes:
#         flight_speed     The maximum speed that such a bird can attain.
#         nesting_grounds  The locale where these birds congregate to reproduce.
#     """
#
#     def get(self):
#         """This function does something.
#
#         :param name: The name to use.
#         :type name: str.
#         :param state: Current state to be in.
#         :type state: bool.
#         :returns: int -- the return code.
#         :raises: AttributeError, KeyError
#
#         """
#         return {'hello': 'world'}

example_bp = Blueprint('example_api', __name__)
api = Api(example_bp)


class HelloWorld(Resource):
    """
        Example class to access an unprotected API
    """

    def get(self):
        """ Return example JSON

            :returns: example JSON
        """
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/api/v1.0/hello/', endpoint="ExampleApi")  # Application context
