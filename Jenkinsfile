pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myflaskapp .'
            }
        }
        stage('Run Docker Container') {
            steps {
                sh '''
                    docker stop myflask || true
                    docker rm myflask || true
                    docker run -d -p 5000:5000 --name myflask myflaskapp
                '''
            }
        }
    }
}
