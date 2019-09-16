rm -rf .terraform
rm *.tfstate
rm *.tfstate.backup
terraform init
terraform apply

