# Tapaz Scraper

## Overview
The Tapaz Scraper is a web scraping tool designed to extract data from the Tap.az website. It utilizes Selenium for browser automation and pandas for data manipulation. This project is structured to facilitate easy modifications and enhancements, making it suitable for production use.

## Project Structure
```
tapaz-scraper
├── src
│   ├── __init__.py
│   ├── config.py        # Configuration settings for the scraper
│   ├── scraper.py       # Main scraping logic
│   ├── utils.py         # Utility functions
│   └── main.py          # Entry point for the application
├── tests
│   ├── __init__.py      # Test package initialization
│   └── test_scraper.py   # Unit tests for the scraper
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd tapaz-scraper
pip install -r requirements.txt
```

## Usage
To run the scraper, execute the following command:

```bash
python src/main.py
```

You can modify the configuration settings in `src/config.py` to adjust the scraping parameters, such as URLs and timeouts.

## Testing
To run the unit tests, navigate to the `tests` directory and execute:

```bash
pytest
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.