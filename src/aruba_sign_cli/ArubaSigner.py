#!/usr/bin/env python3
from pathlib import Path
import zipfile
import io
import requests

BASE_URL = "https://arubasign.arubapec.it/asonline"
WS_BASE_URL = "https://arubasign.arubapec.it/asonline-wsserver/asonline"


class ArubaSigner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"
                    " like Gecko) Chrome/151.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://arubasign.arubapec.it",
                "Referer": "https://arubasign.arubapec.it/asonline/",
            }
        )
        self.jsessionid = None

    def init_session(self):
        """Effettua il primo GET e l'inizializzazione del flusso."""
        res = self.session.get(f"{BASE_URL}/")
        res.raise_for_status()
        self.jsessionid = self.session.cookies.get("JSESSIONID")
        if not self.jsessionid:
            raise RuntimeError("Impossibile recuperare JSESSIONID.")

        self.session.post(
            f"{BASE_URL}/clearOnInit", data={"currentDir": self.jsessionid}
        )
        self.session.post(
            f"{BASE_URL}/manager",
            data={
                "currentDir": self.jsessionid,
                "caller": "firma",
                "clientId": "demo",
                "deviceName": "",
            },
        )

    def upload_file(self, file_path: Path):
        """Carica il file tramite Multipart Raw per garantire la massima compatibilità."""
        boundary = "----WebKitFormBoundaryHgMQb3a0Ms0fuZCi"
        file_bytes = file_path.read_bytes()
        body = bytearray()

        # Parte 1: Il file PDF
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                'Content-Disposition: form-data; name="files[]";'
                f' filename="{file_path.name}"\r\n'
            ).encode("utf-8")
        )
        body.extend(b"Content-Type: application/pdf\r\n\r\n")
        body.extend(file_bytes)
        body.extend(b"\r\n")

        # Parte 2: Parametri form-data
        fields = [
            ("file_id", "0"),
            ("caller", "firma"),
            ("clientId", "demo"),
            ("userId", "undefined"),
            ("deviceName", ""),
            ("currentDir", self.jsessionid),
        ]

        for name, value in fields:
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(
                    "utf-8"
                )
            )
            body.extend(f"{value}\r\n".encode("utf-8"))

        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        headers = self.session.headers.copy()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        res = self.session.post(
            f"{BASE_URL}/upload", data=bytes(body), headers=headers
        )
        res.raise_for_status()

        # Check validità PDF
        res_chk = self.session.post(
            f"{BASE_URL}/checkPdf", data={"currentDir": self.jsessionid}
        )
        res_chk.raise_for_status()

    def get_remote_cert_alias(self, user: str, password: str) -> tuple[str, str]:
        """Recupera l'alias del certificato di firma remota dell'utente."""
        url = f"{WS_BASE_URL}//ListRemoteCerts"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        payload = {
            "remoteUser": user,
            "remotePassword": password,
            "remoteDomain": "firma",
            "fiscalCode": "",
        }

        res = self.session.post(url, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

        if data.get("code") != "0000" or not data.get("signers"):
            raise ValueError(f"Errore recupero certificato: {data.get('message')}")

        signer = data["signers"][0]
        alias = signer["certificate"]["alias"]
        remote_user = signer["remoteInfo"]["user"]
        return alias, remote_user

    def execute_signature(
        self, user: str, password: str, alias: str, otp: str, signature_type: int = 1
    ):
        """Appone la firma remota."""
        url = f"{WS_BASE_URL}//RemoteSignature"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        payload = {
            "currentSession": self.jsessionid,
            "signLocalFile": True,
            "signaturesData": [
                {
                    "signatureType": signature_type,
                    "applyTimestamp": False,
                    "timestampType": 0,
                    "tsaUser": "",
                    "tsaPassword": "",
                    "tsaPolicy": "",
                    "padesType": 0,
                    "signatureMode": 0,
                    "nodepath": None,
                }
            ],
            "user": user,
            "domain": "firma",
            "password": password,
            "alias": alias,
            "otp": otp,
        }

        res = self.session.post(url, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data.get("code") not in ["0000", 0]:
            raise RuntimeError(f"Errore durante la firma: {data}")
        return data

    def download_signed_file(self, output_dir: Path):
        """Scarica l'archivio ZIP con il file firmato ed estrae il documento finale."""
        url = f"{BASE_URL}/zipDownload"
        params = {"currentDir": self.jsessionid}
        
        # Header specifici per il download
        headers = self.session.headers.copy()
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

        res = self.session.get(url, params=params, headers=headers)
        res.raise_for_status()

        # Estrazione diretta in memoria dello ZIP
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
            z.extractall(output_dir)
            extracted_files = z.namelist()
            print(f"[+] File scaricato ed estratto con successo in: {output_dir}")
            for f in extracted_files:
                print(f"    -> {f}")

