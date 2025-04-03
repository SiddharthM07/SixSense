provider "aws" {
    region = var.aws_region

}

resource "aws_instance" "ec-2" {

    ami = var.AMI_ID
    instance_type = var.instance_type
    security_groups = var.security_groups
    key_name = var.key_name

    tags = {
        Name = "${var.environment}-instance"
        environment = var.environment
    }
  
}