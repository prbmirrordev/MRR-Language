"""
╔══════════════════════════════════════════════════════════════════╗
║  MRR CLI — Ana Giriş Noktası v1.0                               ║
║                                                                  ║
║  Tüm MRR araçlarını birleştiren merkezi komut arayüzü.          ║
║                                                                  ║
║  Komutlar:                                                       ║
║    python -m interpreter.main run <dosya.mrr>                    ║
║    python -m interpreter.main compile <dosya.mrr>                ║
║    python -m interpreter.main init [proje_adı]                   ║
║    python -m interpreter.main format <dosya.mrr>                 ║
║    python -m interpreter.main pkg <alt_komut> [args]             ║
║    python -m interpreter.main check <dosya.mrr>                  ║
║    python -m interpreter.main repl                               ║
║    python -m interpreter.main version                            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import argparse
import glob
from pathlib import Path

MRR_VERSION = "1.0.0"
MRR_CODENAME = "Shadow"

from interpreter.mrr_lexer import Lexer
from interpreter.mrr_parser import Parser
from interpreter.mrr_evaluator import Evaluator
from interpreter.mrr_ffi import FFIBridge, SandboxPolicy


def run_file(file_path: str, debug: bool = False):
    """Belirtilen MRR dosyasını anında çalıştırır (Interpreter Mode)."""
    if not os.path.exists(file_path):
        print(f"[HATA] Dosya bulunamadı: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # 1. Lexical Analysis
    lexer = Lexer(source_code, file_path)
    tokens = lexer.tokenize()
    
    if lexer.has_errors:
        print(f"[LEXER HATALARI] {file_path}")
        for err in lexer.errors:
            print(f"  - {err}")
        sys.exit(1)

    if debug:
        print("[DEBUG] Token Akışı:")
        for t in tokens:
            print(f"  {t}")

    # 2. Syntax Analysis (Parsing)
    parser = Parser(tokens)
    ast = parser.parse()

    if parser.has_errors:
        print(f"[PARSER HATALARI] {file_path}")
        for err in parser.errors:
            print(f"  - {err}")
        sys.exit(1)

    # 3. Execution (Evaluation)
    sandbox_policy = SandboxPolicy(
        max_memory_mb=256,
        timeout_seconds=30,
        allow_network=True,
        allow_filesystem=True
    )
    ffi_bridge = FFIBridge(policy=sandbox_policy)
    
    evaluator = Evaluator()
    evaluator.ffi_bridge = ffi_bridge

    try:
        if debug:
            print("[DEBUG] AST Çalıştırılıyor...")
        
        evaluator.execute(ast)
        
        if debug:
            print("\n[DEBUG] Güvenlik Denetim Günlüğü:")
            for log in ffi_bridge.get_audit_log():
                print(f"  - {log}")
                
    except Exception as e:
        print(f"\n{e}")
        sys.exit(1)


def compile_file(file_path: str, obfuscate: bool = True, sign: bool = True):
    """Dosyayı derleme modunda çalıştırır."""
    try:
        from compiler.pipeline.build_pipeline import build_executable
        build_executable(file_path, obfuscate=obfuscate, sign=sign)
    except ImportError:
        print("[HATA] Derleme pipeline'ı bulunamadı.")
        print("[BİLGİ] Interpreter modunu kullanın: mrr run <dosya.mrr>")
        sys.exit(1)


def init_project(name: str = None):
    """Yeni MRR projesi oluştur."""
    from interpreter.mrr_pkg import PackageManager
    pm = PackageManager()
    pm.init(name)


def format_files(files: list, check_only: bool = False):
    """MRR dosyalarını formatla."""
    from interpreter.mrr_formatter import format_file_cli
    
    exit_code = 0
    expanded_files = []
    
    for pattern in files:
        matches = glob.glob(pattern)
        if matches:
            expanded_files.extend(matches)
        else:
            expanded_files.append(pattern)
    
    if not expanded_files:
        print("[HATA] Dosya belirtilmedi: mrr format <dosya.mrr>")
        sys.exit(1)
    
    for filepath in expanded_files:
        if not filepath.endswith('.mrr'):
            continue
        result = format_file_cli(filepath, check_only=check_only)
        if result != 0:
            exit_code = 1
    
    sys.exit(exit_code)


def check_file(file_path: str):
    """Syntax kontrolü — derleme olmadan."""
    if not os.path.exists(file_path):
        print(f"[HATA] Dosya bulunamadı: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Lexical Analysis
    lexer = Lexer(source_code, file_path)
    tokens = lexer.tokenize()
    
    errors = []
    
    if lexer.has_errors:
        for err in lexer.errors:
            errors.append(f"[LEXER] {err}")

    # Syntax Analysis
    parser = Parser(tokens)
    parser.parse()

    if parser.has_errors:
        for err in parser.errors:
            errors.append(f"[PARSER] {err}")

    if errors:
        print(f"✗ {file_path} — {len(errors)} hata bulundu:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"✓ {file_path} — sorun bulunamadı")


def show_version():
    """Sürüm bilgisi göster."""
    print(f"""
╔══════════════════════════════════════════════════╗
║  MRR — Memory, Registers, Rings                 ║
║  Version: {MRR_VERSION} ({MRR_CODENAME})                      ║
║  Offensive Security Programming Language         ║
╚══════════════════════════════════════════════════╝

  Interpreter: Python {sys.version.split()[0]}
  Platform:    {sys.platform}
  Encoding:    UTF-8
""")


def start_repl():
    """İnteraktif REPL başlat."""
    from interpreter.mrr_repl import start_repl as _start
    _start()


def main():
    parser = argparse.ArgumentParser(
        description="MRR Programming Language CLI v" + MRR_VERSION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  mrr run hello.mrr              Dosyayı çalıştır
  mrr format *.mrr               Tüm dosyaları formatla
  mrr init my_project            Yeni proje oluştur
  mrr pkg install scanner        Paket yükle
  mrr check vuln_scanner.mrr     Syntax kontrolü
  mrr version                    Sürüm bilgisi
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # ── run ──
    run_parser = subparsers.add_parser("run", help="MRR dosyasını çalıştır (Interpreter)")
    run_parser.add_argument("file", help="Çalıştırılacak .mrr dosyası")
    run_parser.add_argument("--debug", action="store_true", help="Token ve AST loglarını göster")

    # ── compile ──
    compile_parser = subparsers.add_parser("compile", help="MRR dosyasını makine koduna derle")
    compile_parser.add_argument("file", help="Derlenecek .mrr dosyası")
    compile_parser.add_argument("--no-obfuscate", action="store_true")
    compile_parser.add_argument("--no-sign", action="store_true")

    # ── init ──
    init_parser = subparsers.add_parser("init", help="Yeni MRR projesi oluştur")
    init_parser.add_argument("name", nargs="?", default=None, help="Proje adı")

    # ── format ──
    format_parser = subparsers.add_parser("format", help="Kodu formatla")
    format_parser.add_argument("files", nargs="+", help="Formatlanacak .mrr dosyaları")
    format_parser.add_argument("--check", action="store_true", help="Sadece kontrol et, değiştirme")

    # ── fmt (format kısayolu) ──
    fmt_parser = subparsers.add_parser("fmt", help="format komutunun kısayolu")
    fmt_parser.add_argument("files", nargs="+", help="Formatlanacak .mrr dosyaları")
    fmt_parser.add_argument("--check", action="store_true")

    # ── pkg ──
    pkg_parser = subparsers.add_parser("pkg", help="Paket yöneticisi")
    pkg_parser.add_argument("pkg_args", nargs="*", help="Paket yöneticisi argümanları")

    # ── check ──
    check_parser = subparsers.add_parser("check", help="Syntax kontrolü (derlemesiz)")
    check_parser.add_argument("file", help="Kontrol edilecek .mrr dosyası")

    # ── repl ──
    subparsers.add_parser("repl", help="İnteraktif REPL terminali")

    # ── version ──
    # ── lsp ──
    subparsers.add_parser("lsp", help="Language Server Protocol sunucusunu başlatır")

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file, debug=args.debug)
    elif args.command == "compile":
        compile_file(args.file, not args.no_obfuscate, not args.no_sign)
    elif args.command == "init":
        init_project(args.name)
    elif args.command in ("format", "fmt"):
        format_files(args.files, check_only=args.check)
    elif args.command == "pkg":
        from interpreter.mrr_pkg import pkg_cli
        sys.exit(pkg_cli(args.pkg_args or []))
    elif args.command == "check":
        check_file(args.file)
    elif args.command == "repl":
        start_repl()
    elif args.command == "version":
        show_version()
    elif args.command == "lsp":
        from interpreter.lsp.server import main as lsp_main
        sys.exit(lsp_main())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
