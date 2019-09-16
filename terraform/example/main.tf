terraform {
    backend "http" {
        address = "http://localhost:9090/get/department/product/environment.tf"
        lock_address = "http://localhost:9090/lock/department/product/environment.tf"
        unlock_address = "http://localhost:9090/unlock/department/product/environment.tf"
        # basic auth
        # username =
        # password =
    }
}

locals {
    foo = "bar"
}

data "null_data_source" "self" {
    inputs = {
        foo = "${local.foo}-xx"
    }
}
