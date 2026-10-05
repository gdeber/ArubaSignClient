#!/usr/bin/env python3
import argparse
import getpass
from pathlib import Path
import sys

from .ArubaSigner import ArubaSigner


def main():
    parser = argparse.ArgumentParser(description="CLI per Firma Digitale Remota Aruba")
    parser.add_argument("file", type=str, help="Percorso del file PDF da firmare")
    parser.add_argument("-u", "--user", type=str, help="Username o Codice Fiscale Firma Remota")
    parser.add_argument("-p", "--password", type=str, help="Password Firma Remota")
    parser.add_argument("-o", "--otp", type=str, help="Codice OTP (App/SMS)")
    parser.add_argument("-out", "--output-dir", type=str, help="Directory di destinazione per il file firmato")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[-] Errore: File non trovato '{file_path}'")
        sys.exit(1)

    # se l'utente non ha specificato la directory di output, utilizza la directory del file di input
    if args.output_dir == None:
        args.output_dir = str(file_path.parent)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    user = args.user or input("Username / Codice Fiscale: ")
    password = args.password or getpass.getpass("Password Firma Remota: ")

    signer = ArubaSigner()

    try:
        print("[*] Inizializzazione sessione ed esecuzione upload...")
        signer.init_session()
        signer.upload_file(file_path)

        print("[*] Autenticazione e recupero certificato...")
        alias, remote_user = signer.get_remote_cert_alias(user, password)

        otp = args.otp or input("Inserisci il codice OTP: ")

        print("[*] Applicazione della firma digitale...")
        signer.execute_signature(remote_user, password, alias, otp)

        print("[*] Scaricamento del file firmato...")
        signer.download_signed_file(out_dir)

    except Exception as e:
        print(f"\n[-] Errore durante la procedura: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()