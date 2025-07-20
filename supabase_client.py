from supabase import create_client

SUPABASE_URL = "https://foeeowwctewflhnjqrit.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZvZWVvd3djdGV3Zmxobmpxcml0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwMjIzNzEsImV4cCI6MjA2ODU5ODM3MX0.Ff_WndSZj8LCEIYgkvvkxd3Hn7b97e_y5tINw-kzUVw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_event(event):
    data = {
        "title": event['title'],
        "description": event['description'],
        "category": event['category'],
        "event_date": event['date'],
        "event_time": event['time'],
        "user_email": event['email']
    }
    response = supabase.table("events").insert(data).execute()
    return response