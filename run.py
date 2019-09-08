from src.backend.api_service import APIService

app = APIService.get()

if __name__ == '__main__':
    app.run()
