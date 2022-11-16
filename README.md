
# Instruction lab04


## A. Download:

```
git clone https://github.com/KaterynaShcherbakova/labs_ap
```

## B. Check current python version:

```
python -V
```

_If not **3.7.\*** :_

``` 
pyenv install 3.7.*
```
 
*Set local version of python:*
```
pyenv local 3.7.x
```

## C. Init virtual environment:

*Create virtual environment:*
```
python -m venv venv
```

*Activate venv:*
```
venv\Scripts\activate
```

*Install Flask and Waitress:*
```
pip install -r requirements.txt
```


## D. Run a server:

```
waitress-serve --host 127.0.0.1 main:app 
flask --app main --debug run
```


## [Link](http://127.0.0.1:5000/api/v1/hello-world-29)
