from flask import Blueprint, current_app, jsonify, render_template, request

from services.etiket_ekrani_service import (
    VARSAYILAN_AYARLAR,
    YAZI_TIPLERI,
    ayarlari_getir,
    ayarlari_kaydet,
    etiket_bas,
    urunleri_getir,
)

bp = Blueprint("etiket_ekrani", __name__)


def _hata(mesaj, kod):
    return jsonify({"error": mesaj}), kod


@bp.route("/etiket-ekrani")
def sayfa():
    return render_template(
        "etiket_ekrani.html",
        yazi_tipleri=YAZI_TIPLERI,
        varsayilan_ayarlar=VARSAYILAN_AYARLAR,
    )


@bp.route("/api/etiket-ekrani/urunler")
def urunler():
    try:
        return jsonify(urunleri_getir())
    except Exception:
        current_app.logger.exception("etiket_ekrani: urunler okunamadi")
        return _hata("Ürün listesi yüklenemedi. Lütfen sayfayı yenileyin.", 500)


@bp.route("/api/etiket-ekrani/ayarlar", methods=["GET"])
def ayarlar_oku():
    try:
        return jsonify(ayarlari_getir())
    except Exception:
        current_app.logger.exception("etiket_ekrani: ayarlar okunamadi")
        return _hata("Etiket ayarları okunamadı. Varsayılan ayarlar kullanılabilir.", 500)


@bp.route("/api/etiket-ekrani/ayarlar", methods=["POST"])
def ayarlar_yaz():
    gelen = request.get_json(silent=True)
    if not isinstance(gelen, dict) or not gelen:
        return _hata("Kaydedilecek ayar gönderilmedi.", 400)
    try:
        ayarlari_kaydet(ayarlar=gelen)
    except ValueError:
        return _hata("Gönderilen ayarlar geçersiz. Değerleri kontrol edin.", 400)
    except Exception:
        current_app.logger.exception("etiket_ekrani: ayarlar kaydedilemedi")
        return _hata("Ayarlar kaydedilemedi. Lütfen tekrar deneyin.", 500)
    return jsonify({"ok": True, "mesaj": "Ayarlar kaydedildi"})


@bp.route("/api/etiket-ekrani/bas", methods=["POST"])
def bas():
    gelen = request.get_json(silent=True)
    etiketler = gelen.get("etiketler") if isinstance(gelen, dict) else None
    if not isinstance(etiketler, list) or not etiketler:
        return _hata("En az bir ürün seçmelisiniz.", 400)
    if not all(isinstance(et, dict) and et.get("id") and et.get("fiyat") for et in etiketler):
        return _hata("Her etiket için ürün ve fiyat gerekli.", 400)

    try:
        sonuclar = [
            etiket_bas(
                str(et.get("id", "")),
                str(et.get("ad", "")),
                str(et.get("fiyat", "")),
                str(et.get("birim", "")),
                str(et.get("fiyat_tarihi", "")),
            )
            for et in etiketler
        ]
    except Exception:
        current_app.logger.exception("etiket_ekrani: basim gonderilemedi")
        return _hata("Etiketler yazıcıya gönderilemedi. Lütfen tekrar deneyin.", 500)

    return jsonify({
        "ok": True,
        "mesaj": f"{len(etiketler)} etiket basım komutu gönderildi",
        "sonuclar": sonuclar,
    })
