# HyperSpin

HyperSpin is a modern Point of Sale (POS) and Inventory Management system built with [Flet](https://flet.dev) and [SQLModel](https://sqlmodel.tiangolo.com/).

## Features

- **Inventory Management**: Track products, quantities, prices, and stock status.
- **Modern UI**: A beautiful and responsive user interface built with Flet.
- **Local Database**: Uses SQLite for easy deployment and data management.
- **Future Features**:
    - Sales & Payments (Cash Register)
    - User Management & Authorization
    - Detailed Logging & Analytics

## Project Structure

```
src/
    main.py             # Entry point of the application
    assets/             # Static assets (images, icons)
    components/         # UI Components (Product lists, forms)
    controllers/        # Business logic and database interactions
    db/                 # Database connection and configuration
    models/             # SQLModel database models
storage/
    data/               # Database file location
    temp/               # Temporary files
```

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation

1.  Clone the repository.
2.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    # OR if using uv/poetry as per pyproject.toml
    uv sync
    ```

### Running the App

```bash
flet run src/main.py
```


## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).