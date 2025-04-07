# 📅 Eventify CalendarApp

**Eventify** is a simple and modern desktop calendar application built with Python and Tkinter. It enables users to manage local events with ease using a user-friendly interface.

## ✨ Features

- Interactive calendar with visual event markers
- Add, edit, and delete events with:
  - Title
  - Date and Time
  - Description
- Daily event view sorted by time
- Local event data persistence using JSON
- Clean and responsive UI using `ttk` and `tkcalendar`

## 🛠️ Built With

- **Python 3.7+**
- **Tkinter** – for GUI development
- **tkcalendar** – for calendar widgets

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.7 or above installed.

Install required dependencies:

```bash
pip install tkcalendar
```

### Run the App

Clone the repository and run the main script:

```bash
git clone https://github.com/eduolihez/Eventify-CalendarApp.git
cd Eventify-CalendarApp
python main.py
```

## 📁 Project Structure

```
Eventify-CalendarApp/
│
├── main.py                # Main application script
├── calendar.db            # Local SQLite database for storing events
├── /database              # Database interaction logic
├── /ui                    # GUI components
├── /utils                 # Utility modules (e.g., validation, formatting)
├── README.md
└── LICENSE
```

## 👨‍💻 Author

Created and maintained by [Edu Olivares](https://github.com/eduolihez).  
This project covers basic calendar features – feel free to fork it and add more!

## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## ⭐ Contributing

Contributions are welcome! If you’d like to add features or fix bugs:

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📌 Acknowledgments

Thanks to the developers of `tkcalendar` and the Python open-source community for their amazing work.

---

Feel free to share feedback, ideas, or suggestions. Happy calendaring!
