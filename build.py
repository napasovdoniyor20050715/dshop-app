#!/usr/bin/env python3
"""
Bu fayl Render.com da deploy bo'lganda bir marta ishga tushadi.
Jadvallarni yaratadi va demo ma'lumotlar qo'shadi.
"""
from app import app, create_tables

if __name__ == '__main__':
    print("Jadvallar yaratilmoqda...")
    create_tables()
    print("Tayyor! Jadvallar va demo ma'lumotlar yaratildi.")
    print("Admin kirish: username=admin, parol=admin123")
