#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drive_store.py  -  optional Google Drive auto-save for FlowCast.

Uses a Google *service account* (no interactive login). You:
  1. Create a service account + JSON key in Google Cloud.
  2. Enable the Drive API.
  3. Share a Google Drive folder with the service account's email.
  4. Put the key + folder id into Streamlit secrets (see README_GOOGLE_DRIVE).

If secrets aren't configured, every function reports "not configured" and the
app silently falls back to manual download/upload. Nothing here ever crashes
the app.

Talks to the Drive REST API directly with an authorized session, so the only
dependencies are google-auth + requests (already available on Streamlit Cloud).
"""
import json
import datetime

DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"
DRIVE_FILES = "https://www.googleapis.com/drive/v3/files"
SCOPES = ["https://www.googleapis.com/auth/drive"]

# The filename we store the plan under, inside the shared folder.
PLAN_FILENAME = "flowcast_plan.json"


def _get_secrets(st):
    """Return (creds_dict, folder_id) or (None, None) if not configured."""
    try:
        if "gcp_service_account" not in st.secrets:
            return None, None
        creds = dict(st.secrets["gcp_service_account"])
        folder_id = st.secrets.get("drive_folder_id", None)
        if not creds or not folder_id:
            return None, None
        return creds, folder_id
    except Exception:
        return None, None


def is_configured(st):
    creds, folder = _get_secrets(st)
    return creds is not None and folder is not None


def _session(creds_dict):
    from google.oauth2 import service_account
    import google.auth.transport.requests as gtr
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    session = gtr.AuthorizedSession(creds)
    return session


def _find_file_id(session, folder_id, filename=PLAN_FILENAME):
    q = "name='%s' and '%s' in parents and trashed=false" % (filename, folder_id)
    r = session.get(DRIVE_FILES, params={
        "q": q, "fields": "files(id,name,modifiedTime)", "spaces": "drive",
        "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
    }, timeout=20)
    r.raise_for_status()
    files = r.json().get("files", [])
    return files[0]["id"] if files else None


def load(st):
    """Return (model_dict, status_msg). model is None if nothing to load."""
    creds, folder_id = _get_secrets(st)
    if not creds:
        return None, "Drive not configured."
    try:
        session = _session(creds)
        fid = _find_file_id(session, folder_id)
        if not fid:
            return None, "No saved plan in Drive yet."
        r = session.get(DRIVE_FILES + "/" + fid,
                        params={"alt": "media", "supportsAllDrives": "true"}, timeout=20)
        r.raise_for_status()
        return json.loads(r.content.decode("utf-8")), "Loaded from Google Drive."
    except Exception as exc:
        return None, "Drive load failed: %s" % exc


def save(st, model):
    """Create or update flowcast_plan.json in the shared folder.
    Returns (ok_bool, status_msg)."""
    creds, folder_id = _get_secrets(st)
    if not creds:
        return False, "Drive not configured."
    try:
        session = _session(creds)
        fid = _find_file_id(session, folder_id)
        payload = json.dumps(model, indent=2).encode("utf-8")
        if fid:
            # update existing file contents
            r = session.patch(
                DRIVE_UPLOAD + "/" + fid,
                params={"uploadType": "media", "supportsAllDrives": "true"},
                data=payload,
                headers={"Content-Type": "application/json"}, timeout=30)
            r.raise_for_status()
        else:
            # multipart create with metadata + content
            metadata = {"name": PLAN_FILENAME, "parents": [folder_id]}
            boundary = "flowcastboundary1234567890"
            body = (
                ("--%s\r\n" % boundary).encode()
                + b"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                + json.dumps(metadata).encode() + b"\r\n"
                + ("--%s\r\n" % boundary).encode()
                + b"Content-Type: application/json\r\n\r\n"
                + payload + b"\r\n"
                + ("--%s--\r\n" % boundary).encode()
            )
            r = session.post(
                DRIVE_UPLOAD,
                params={"uploadType": "multipart", "supportsAllDrives": "true"},
                data=body,
                headers={"Content-Type": "multipart/related; boundary=%s" % boundary},
                timeout=30)
            r.raise_for_status()
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        return True, "Saved to Google Drive at %s." % stamp
    except Exception as exc:
        return False, "Drive save failed: %s" % exc


def backup(st, model):
    """Write a dated backup copy (never overwrites). Returns (ok, msg)."""
    creds, folder_id = _get_secrets(st)
    if not creds:
        return False, "Drive not configured."
    try:
        session = _session(creds)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        name = "flowcast_backup_%s.json" % stamp
        metadata = {"name": name, "parents": [folder_id]}
        payload = json.dumps(model, indent=2).encode("utf-8")
        boundary = "flowcastboundary1234567890"
        body = (
            ("--%s\r\n" % boundary).encode()
            + b"Content-Type: application/json; charset=UTF-8\r\n\r\n"
            + json.dumps(metadata).encode() + b"\r\n"
            + ("--%s\r\n" % boundary).encode()
            + b"Content-Type: application/json\r\n\r\n"
            + payload + b"\r\n"
            + ("--%s--\r\n" % boundary).encode()
        )
        r = session.post(
            DRIVE_UPLOAD,
            params={"uploadType": "multipart", "supportsAllDrives": "true"},
            data=body,
            headers={"Content-Type": "multipart/related; boundary=%s" % boundary},
            timeout=30)
        r.raise_for_status()
        return True, "Backup '%s' written to Drive." % name
    except Exception as exc:
        return False, "Drive backup failed: %s" % exc
