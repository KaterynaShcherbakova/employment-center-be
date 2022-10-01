# from itertools import product
#
# student_id = 29
# print(list(product(
#     ('python 3.8.*', 'python 3.7.*', 'python 3.6.*'),
#     ('venv + requirements.txt', 'virtualenv + requirements.txt', 'poetry', 'pipenv')
# ))[(student_id - 1) % 12])

import sys
from flask import Flask

# print("Hello", sys.version)

app = Flask(__name__)


@app.route('/api/v1/hello-world-29')
def func():
    return "Hello World 29", 200


app.run()
