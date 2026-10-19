# -*- coding: utf-8 -*-
"""Vercel/WSGI এন্ট্রিপয়েন্টের টেস্ট (Flask test client, নেটওয়ার্ক ছাড়া)।"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app  # noqa: E402


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_validate_route():
    client = app.test_client()
    response = client.post("/validate", json={"text": "সাল 2020"})
    assert response.status_code == 200
    report = response.get_json()["report"]
    assert report["valid"] is False
    assert report["rules"]["২"]["ok"] is False


def test_fix_route_without_mt():
    client = app.test_client()
    response = client.post("/fix", json={"text": "[[Category:Films]]", "translate": False})
    assert response.status_code == 200
    assert response.get_json()["fixed"] == "[[বিষ" + "\u09df" + "শ্রেণী:Films]]"


def test_dashboard_served():
    client = app.test_client()
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data


def test_preview_empty_is_ok():
    client = app.test_client()
    response = client.post("/preview", json={"text": ""})
    assert response.status_code == 200
    assert response.get_json()["ok"] is True
