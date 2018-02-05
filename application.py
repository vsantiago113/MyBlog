from app import app as application

if __name__ == "__main__":
    application.run(host=application.config.get("HOST"),
                    port=application.config.get("PORT"))
