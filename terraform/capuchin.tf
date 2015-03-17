provider "aws" {
    access_key = "${var.aws_access_key}"
    secret_key = "${var.aws_secret_key}"
    region = "${var.aws_region}"
}

resource "aws_vpc" "capuchin_vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support = true
    tags {
        Name = "capuchin"
    }
}

resource "aws_subnet" "capuchin_public_subnet" {
    vpc_id = "${aws_vpc.capuchin_vpc.id}"
    cidr_block = "10.0.0.0/24"

    tags {
        Name = "capuchin_public_subnet"
    }
}

resource "aws_internet_gateway" "capuchin_igw" {
    vpc_id = "${aws_vpc.capuchin_vpc.id}"

    tags {
        Name = "capuchin_igw"
    }
}

resource "aws_route_table" "capuchin_public_rt" {
    vpc_id = "${aws_vpc.capuchin_vpc.id}"

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.capuchin_igw.id}"
    }

    tags {
        Name = "capuchin_public_rt"
    }
}

resource "aws_route_table_association" "capuchin_public_rta" {
    subnet_id = "${aws_subnet.capuchin_public_subnet.id}"
    route_table_id = "${aws_route_table.capuchin_public_rt.id}"
}

resource "aws_security_group" "capuchin_app_sg" {
    name = "allow_all"
    description = "Allow all inbound traffic"
    vpc_id = "${aws_vpc.capuchin_vpc.id}"

    ingress{
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags {
        Name = "capuchin_app_sg"
    }
}

resource "aws_instance" "capuchin_app" {
    ami = "ami-167d5f7e"
    instance_type = "m1.medium"
    subnet_id = "${aws_subnet.capuchin_public_subnet.id}"
    security_groups = [
        "${aws_security_group.capuchin_app_sg.id}",
    ]

    key_name = "devops"
    user_data = "${file(\"./user_data.yml\")}"
    tags {
        Name = "capuchin_app"
    }
}

resource "aws_eip" "capuchin_app_eip" {
    instance = "${aws_instance.capuchin_app.id}"
    vpc = true
}
