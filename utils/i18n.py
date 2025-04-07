import os
import gettext
import locale

class I18nManager:
    """Manages internationalization and localization"""
    
    def __init__(self, lang_code='en'):
        """Initialize the internationalization manager"""
        self.lang_code = lang_code
        self.translations = {}
        
        # Load translations
        self.load_translations()
        
        # Set the current translation
        self.set_language(lang_code)
    
    def load_translations(self):
        """Load all available translations"""
        # English is the default language (no translation needed)
        self.translations['en'] = gettext.NullTranslations()
        
        # Spanish translation
        self.translations['es'] = self.create_spanish_translation()
    
    def create_spanish_translation(self):
        """Create a simple Spanish translation dictionary"""
        # This is a simplified approach without .mo files
        # In a real application, you would use proper gettext .mo files
        spanish_dict = {
            "Calendar & Event Manager": "Calendario y Gestor de Eventos",
            "Add Event": "Añadir Evento",
            "Edit Event": "Editar Evento",
            "Delete": "Eliminar",
            "Save": "Guardar",
            "Cancel": "Cancelar",
            "Title": "Título",
            "Description": "Descripción",
            "Start Time": "Hora de Inicio",
            "End Time": "Hora de Fin",
            "Location": "Ubicación",
            "Priority": "Prioridad",
            "Low": "Baja",
            "Medium": "Media",
            "High": "Alta",
            "Color": "Color",
            "Choose Color": "Elegir Color",
            "Recurring": "Recurrente",
            "This is a recurring event": "Este es un evento recurrente",
            "Recurrence Options": "Opciones de Recurrencia",
            "Repeat": "Repetir",
            "Daily": "Diario",
            "Weekly": "Semanal",
            "Monthly": "Mensual",
            "Yearly": "Anual",
            "End Recurrence": "Fin de Recurrencia",
            "Date": "Fecha",
            "Time": "Hora",
            "Today": "Hoy",
            "Month": "Mes",
            "Week": "Semana",
            "Search": "Buscar",
            "Import Events": "Importar Eventos",
            "Export Events": "Exportar Eventos",
            "File": "Archivo",
            "Edit": "Editar",
            "View": "Ver",
            "Help": "Ayuda",
            "About": "Acerca de",
            "Theme": "Tema",
            "Light Theme": "Tema Claro",
            "Dark Theme": "Tema Oscuro",
            "Language": "Idioma",
            "Go to Today": "Ir a Hoy",
            "Search Events": "Buscar Eventos",
            "Search Results": "Resultados de Búsqueda",
            "No events found matching": "No se encontraron eventos que coincidan con",
            "Open Event": "Abrir Evento",
            "Close": "Cerrar",
            "Import Successful": "Importación Exitosa",
            "Export Successful": "Exportación Exitosa",
            "events were imported successfully": "eventos fueron importados con éxito",
            "events were exported successfully": "eventos fueron exportados con éxito",
            "No events to export": "No hay eventos para exportar",
            "Export Format": "Formato de Exportación",
            "Do you want to export as iCalendar (.ics)?": "¿Desea exportar como iCalendar (.ics)?",
            "Selecting 'No' will export as CSV.": "Seleccionar 'No' exportará como CSV.",
            "iCalendar Files": "Archivos iCalendar",
            "CSV Files": "Archivos CSV",
            "All Files": "Todos los Archivos",
            "Error": "Error",
            "Title is required": "El título es obligatorio",
            "End time must be after start time": "La hora de fin debe ser posterior a la hora de inicio",
            "Success": "Éxito",
            "Event updated successfully": "Evento actualizado con éxito",
            "Event created successfully": "Evento creado con éxito",
            "Confirm Deletion": "Confirmar Eliminación",
            "Are you sure you want to delete this event?": "¿Está seguro de que desea eliminar este evento?",
            "Event History": "Historial del Evento",
            "No history found for this event": "No se encontró historial para este evento",
            "Timestamp": "Marca de Tiempo",
            "Action": "Acción",
            "Details": "Detalles",
            "Select Date": "Seleccionar Fecha",
            "Year": "Año",
            "Mon": "Lun",
            "Tue": "Mar",
            "Wed": "Mié",
            "Thu": "Jue",
            "Fri": "Vie",
            "Sat": "Sáb",
            "Sun": "Dom",
            "Calendar Event Reminder": "Recordatorio de Evento de Calendario",
            "Event at": "Evento a las",
            "Dismiss": "Descartar",
            "History": "Historial",
            "Events for": "Eventos para",
            "Ready": "Listo",
            "Language Changed": "Idioma Cambiado",
            "Please restart the application for the language change to take full effect.": "Por favor, reinicie la aplicación para que el cambio de idioma surta efecto por completo.",
            "About Calendar & Event Manager": "Acerca de Calendario y Gestor de Eventos",
            "A feature-rich desktop calendar application": "Una aplicación de calendario de escritorio con múltiples funciones",
            "Version 1.0.0": "Versión 1.0.0",
            "+ {} more": "+ {} más",
            "Do you want to export all events?": "¿Desea exportar todos los eventos?",
            "Selecting 'No' will export only events in the current view.": "Seleccionar 'No' exportará solo los eventos en la vista actual."
        }
        
        # Create a custom translation class
        class CustomTranslation(gettext.NullTranslations):
            def __init__(self, translation_dict):
                self.translation_dict = translation_dict
            
            def gettext(self, message):
                return self.translation_dict.get(message, message)
        
        return CustomTranslation(spanish_dict)
    
    def set_language(self, lang_code):
        """Set the current language"""
        if lang_code in self.translations:
            self.lang_code = lang_code
            self.current_translation = self.translations[lang_code]
        else:
            # Default to English
            self.lang_code = 'en'
            self.current_translation = self.translations['en']
        
        # Set the gettext translation
        self.gettext = self.current_translation.gettext