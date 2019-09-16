# terraform-backend-sample

A sample python wsgi module to implement a custom Terraform backend

# Running

* create a virtual env `python3 -m virtualenv venv`
* activate your virtual env `. venv/bin/activate`
* install required packages into your virtual env `pip install -r requirements.txt`
* test with pytest `pytest . -v`
* run with gunicorn or uwsgi `uwsgi --http :9090 --wsgi-file tfbackend/wsgi.py --callable app`
* DO NOT USE WITH PRODUCTION INFRASTRUCTURE
* terraform side, in a sample repo (NOT PRODUCTION), configure backend.tf to point to your running instance

```terraform
backend "http" {
    address = http://localhost:9090/get/department/product/environment.tf
    lock_address = http://localhost:9090/lock/department/product/environment.tf
    unlock_address = http://localhost:9090/unlock/department/product/environment.tf
    # basic auth
    # username =
    # password =
}
```

# Customizing

* in this sample application, the data is stored in memory and is lost when the process is closed, so redirect calls to a database
* add security with user/password passed in basic auth
* add ssl
