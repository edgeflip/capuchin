provider "aws" {
    access_key = "${var.access_key}"
    secret_key = "${var.secret_key}"
    region = "${var.region}"
}

resource "aws_security_group" "ssh" {
    name = "capuchin ssh"
    description = "Used in the terraform"

    # SSH access from anywhere
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_instance" "capuchin" {
    ami = "${lookup(var.amis, var.region)}"
    instance_type = "t2.medium"
    key_name = "devops"
    security_groups =[
        "${aws_security_group.ssh.name}"
    ]
    connection {
        # The default username for our AMI
        user = "ubuntu"

        # The path to your keyfile
        key_file = "${var.key_path}"
    }

    provisioner "file" {
        source = "./.ssh"
        destination = "/home/ubuntu"
    }

    provisioner "remote-exec" {
        inline = [
            "sudo apt-get install nginx --yes",
            "sudo chmod 700 /home/ubuntu/.ssh",
            "sudo chmod 600 /home/ubuntu/.ssh/id_rsa",
            "sudo chmod 644 /home/ubuntu/.ssh/id_rsa.pub",
            "sudo apt-get update",
            "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9",
            "sudo sh -c 'echo deb https://get.docker.com/ubuntu docker main /etc/apt/sources.list.d/docker.list'",
            "sudo apt-get update",
            "curl -sSL https://get.docker.com/ubuntu/ | sudo sh",
            "sudo apt-get install git --yes",
            "sudo apt-get install wget --yes",
            "wget https://bootstrap.pypa.io/get-pip.py",
            "sudo python get-pip.py",
            "sudo pip install fig",
            "ssh-keyscan github.com >> ~/.ssh/known_hosts",
            "git clone ${var.git_repo}",
            "cd ${var.app}",
            "sudo rm /etc/nginx/sites-enabled/default",
            "sudo cp ./config/nginx /etc/nginx/sites-enabled/capuchin.conf",
            "sudo service nginx reload",
            "sudo fig up -d"
        ]
    }
}

resource "aws_elb" "web" {
    name = "capuchin-elb"

    # The same availability zone as our instance
    availability_zones = ["${aws_instance.capuchin.availability_zone}"]

    listener {
        instance_port = 80
        instance_protocol = "http"
        lb_port = 80
        lb_protocol = "http"
    }

    # The instance is registered automatically
    instances = ["${aws_instance.capuchin.id}"]
}
