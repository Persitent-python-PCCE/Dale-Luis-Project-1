pipeline {
    agent any

    triggers{
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    ./venv/bin/pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t dale09/flask-app:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-creds1',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push dale09/flask-app:latest
                    '''
                }
            }
        }
    }
    post{
        success{
            emailext(
                subject: "Success: ${env.JOB_NAME} BUILD #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins was successful</h1>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "dalerioluis@gmail.com"
            )
        }
        failure{
            emailext(
                subject: "Failure: ${env.JOB_NAME} BUILD #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins Failed</h1>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "dalerioluis@gmail.com"
            )
        }
    }
}