from flask import Flask, render_template, request
import paramiko

app = Flask(__name__)

ssh_client = None

DOCKER_OPTIONS = [
    "docker --version", "docker version", "docker info", "docker login", "docker logout",
    "docker images", "docker pull", "docker rmi", "docker ps", "docker ps -a",
    "docker start", "docker stop", "docker restart", "docker rm", "docker exec",
    "docker logs", "docker inspect", "docker build", "docker run",
    "docker container prune -f", "docker image prune -f", "docker network ls",
    "docker network inspect", "docker network prune -f", "docker volume ls",
    "docker volume inspect", "docker volume prune -f", "date", "Custom command"
]


@app.route("/", methods=["GET", "POST"])
def index():
    global ssh_client

    output = ""
    error = ""

    if request.method == "POST":
        if 'connect' in request.form:
            # Connect SSH
            hostname = request.form.get("hostname")
            username = request.form.get("username")
            password = request.form.get("password")

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh_client.connect(hostname=hostname, username=username, password=password)
                output = "✅ Connected successfully!"
            except Exception as e:
                ssh_client = None
                error = f"❌ SSH connection failed: {e}"

        elif 'disconnect' in request.form:
            if ssh_client:
                ssh_client.close()
                ssh_client = None
                output = "🔌 Disconnected successfully."

        elif 'run' in request.form and ssh_client:
            selected = request.form.get("docker_command")
            command = ""

            if selected == "Custom command":
                command = request.form.get("custom_command")
            elif selected in ["docker stop", "docker start", "docker restart", "docker rm", "docker logs", "docker inspect"]:
                container_id = request.form.get("container_id")
                command = f"{selected} {container_id}"
            elif selected == "docker exec":
                container_id = request.form.get("container_id")
                exec_cmd = request.form.get("exec_cmd")
                command = f"docker exec {container_id} {exec_cmd}"
            elif selected == "docker pull":
                image_name = request.form.get("image_name")
                tag = request.form.get("tag") or "latest"
                command = f"docker pull {image_name}:{tag}"
            elif selected == "docker rmi":
                image_name = request.form.get("image_name")
                tag = request.form.get("tag")
                command = f"docker rmi {image_name}:{tag}" if tag else f"docker rmi {image_name}"
            elif selected == "docker build":
                image_name = request.form.get("image_name")
                tag = request.form.get("tag")
                path = request.form.get("path")
                command = f"docker build -t {image_name}:{tag} {path}"
            elif selected == "docker run":
                image_name = request.form.get("image_name")
                options_run = request.form.get("options_run")
                cmd_inside = request.form.get("cmd_inside")
                command = f"docker run {options_run} {image_name} {cmd_inside}"
            else:
                command = selected

            try:
                stdin, stdout, stderr = ssh_client.exec_command(command, timeout=20)
                stdout.channel.recv_exit_status()
                output = stdout.read().decode() or "(No output)"
                error = stderr.read().decode()
            except Exception as e:
                error = str(e)

    return render_template(
        "index.html",
        options=DOCKER_OPTIONS,
        output=output,
        error=error,
        request=request  # pass request to use sticky fields
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
