"""
Simple test module to verify imports work.
This can be removed once deployment is working.
"""
from flask import Flask

def create_app():
    test_app = Flask(__name__)
    
    @test_app.route('/')
    def hello():
        return "Hello from test app!"
    
    return test_app

# For testing
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)