from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)                 # Debug reruns server on change to code, turn off in production mode 