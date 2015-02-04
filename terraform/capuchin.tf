provider "aws" {
    access_key = "${var.aws_access_key}"
    secret_key = "${var.aws_secret_key}"
    region = "${var.aws_region}"
}

module "vpc" {
    source = "github.com/entone/terraform-aws-vpc"
    network = "10.0"
    aws_key_name = "devops"
    aws_access_key = "${var.aws_access_key}"
    aws_secret_key = "${var.aws_secret_key}"
    aws_region = "${var.aws_region}"
    aws_key_path = "${var.aws_key_path}"
}

resource "aws_elb" "web" {
    name = "capuchin-elb"

    # The same availability zone as our instance
    availability_zones = ["${aws_instance.capuchin.availability_zone}"]

    subnets = [
        "${module.vpc.bastion_subnet}",
    ]

    listener {
        instance_port = 8000
        instance_protocol = "http"
        lb_port = 80
        lb_protocol = "http"
    }

    health_check {
        healthy_threshold = 2
        unhealthy_threshold = 2
        timeout = 3
        target = "HTTP:8000/"
        interval = 30
    }

    security_groups = [
        "${aws_security_group.web.name}"
    ]

    instances = ["${aws_instance.capuchin.id}"]
}

resource "aws_instance" "capuchin" {
    ami = "${lookup(var.amis, var.aws_region)}"
    instance_type = "t2.medium"
    key_name = "devops"
    subnet_id = "${module.vpc.bastion_subnet}"
    connection {
        # The default username for our AMI
        user = "ubuntu"

        # The path to your keyfile
        key_file = "${var.aws_key_path}"
    }

    user_data = "${file(\"./user_data.txt\")}"

    security_groups = [
        "${module.vpc.aws_security_group_bastion_id}",
    ]
}

resource "aws_security_group" "web" {
    name = "edgflip_public"
    description = "Allows all requests to ELB on port 80"

    # HTTP access from anywhere
    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}
