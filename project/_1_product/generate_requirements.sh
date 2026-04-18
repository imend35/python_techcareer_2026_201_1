#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# requirements.txt oluşturur ve içine verilen paketleri ekler.
# Kullanım:
#   chmod +x generate_requirements.sh
#   ./generate_requirements.sh
#   ./generate_requirements.sh flask requests
#   ./generate_requirements.sh -f my_requirements.txt flask requests
#   ./generate_requirements.sh -f requirements.txt numpy pandas matplotlib beartype
# ============================================================


OUTPUT_FILE="requirements.txt"
DEFAULT_PACKAGES=(
  "numpy"
  "pandas"
  "matplotlib"
  "beartype"
)


print_usage() {
  echo "Kullanım: $0 [-f dosya_adi] [paket1 paket2 paket3 ...]"
  echo
  echo "Örnekler:"
  echo "  $0"
  echo "  $0 flask requests"
  echo "  $0 -f my_requirements.txt numpy pandas matplotlib beartype"
}

# Argümanları işle
PACKAGES=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file)
      if [[ $# -lt 2 ]]; then
        echo "Hata: -f veya --file sonrası dosya adı vermelisin."
        exit 1
      fi
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      PACKAGES+=("$1")
      shift
      ;;
  esac
done



# Eğer kullanıcı paket vermediyse varsayılan paketleri kullan
if [[ ${#PACKAGES[@]} -eq 0 ]]; then
  PACKAGES=("${DEFAULT_PACKAGES[@]}")
fi


# Dosya yoksa oluştur
if [[ ! -f "$OUTPUT_FILE" ]]; then
  touch "$OUTPUT_FILE"
  echo "[OLUŞTURULDU] $OUTPUT_FILE"
else
  echo "[MEVCUT] $OUTPUT_FILE bulundu"
fi



# Paket ekleme fonksiyonu
add_package_if_missing() {
  local package="$1"

  # Baştaki/sondaki boşlukları temizle
  package="$(echo "$package" | xargs)"

  if [[ -z "$package" ]]; then
    return
  fi

  # requirements.txt içinde aynı paket varsa tekrar ekleme
  # Eşleşme: numpy, numpy==1.26.4, numpy>=1.0 gibi satırları kapsar
  if grep -Eq "^${package}([=<>!~].*)?$" "$OUTPUT_FILE"; then
    echo "[ATLANDI] Zaten var: $package"
  else
    echo "$package" >> "$OUTPUT_FILE"
    echo "[EKLENDI] $package"
  fi
}

for package in "${PACKAGES[@]}"; do
  add_package_if_missing "$package"
done

echo

echo "Güncel $OUTPUT_FILE içeriği:"
echo "----------------------------------------"
cat "$OUTPUT_FILE"
echo "----------------------------------------"

