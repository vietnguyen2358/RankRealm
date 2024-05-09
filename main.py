from website import create_app

# flask --app main run --debug 

# Run website with "flask --app main --debug run" <- debug for development purposes. DO NOT run with debug on release

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)                 # Debug reruns server on change to code, turn off in production mode 