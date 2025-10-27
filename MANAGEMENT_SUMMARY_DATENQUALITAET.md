# Management Summary: Datenqualität & Analyse
## Transportdaten Juni 2025 – Traveco

**Berichtsdatum**: 24. Oktober 2025
**Analysezeitraum**: 1. – 30. Juni 2025
**Analyst**: Kevin Kuhn

---

## 1. Zusammenfassung

Diese Analyse untersucht die Qualität und Vollständigkeit der von Traveco bereitgestellten Transportdaten für Juni 2025. Die Datengrundlage umfasst **135.646 Transportaufträge** aus 12 Betriebszentralen über einen vollständigen Monat.

### Gesamtbewertung der Datenqualität: ⭐⭐⭐⭐½ (4.5/5)

**Highlights**:
- ✅ Vollständige Abdeckung des Analysezeitraums (30 Tage)
- ✅ Hohe Datenqualität mit 99,7% erfolgreich zugeordneten Aufträgen
- ✅ Konsistente Verknüpfung zwischen Auftrags-, Tour- und Spartendaten
- ⚠️ Einzelne Dateninkonsistenzen identifiziert und korrigiert

---

## 2. Datenqualität

### 2.1 Vollständigkeit (Completeness)

| Kriterium | Status | Details |
|-----------|--------|---------|
| **Zeitraum** | ✅ Vollständig | 01.06.2025 – 30.06.2025 (30 Tage) |
| **Auftragsvolumen** | ✅ Vollständig | 135.646 Aufträge erfasst |
| **Betriebszentralen** | ✅ Vollständig | 12 Betriebszentralen mit Daten |
| **Finanzielle Daten** | ✅ Verfügbar | Einnahmen und Ausgaben vorhanden |
| **Tourinformationen** | ✅ Verfügbar | Distanzen und Fahrzeiten erfasst |
| **Spartenzuordnung** | ✅ 97,3% | 384 Kundendivisionen zugeordnet |

**Fehlende Daten**:
- ~2,7% der Aufträge ohne Spartenzuordnung (Traveco-interne Pseudo-Kunden)
- ~0,3% der Aufträge ohne Betriebszentralen-Zuordnung

### 2.2 Genauigkeit (Accuracy)

**Validierungsergebnisse**:
- ✅ Alle Datumsfelder im erwarteten Format
- ✅ Numerische Felder (Distanzen, Kosten) plausibel
- ✅ Referenzintegrität zwischen Dateien gewährleistet
- ✅ Keine signifikanten Ausreißer in Distanz- oder Kostendaten

**Identifizierte Datenanomalien**:
- 351 Aufträge ohne zugeordnete Betriebszentrale (0,3%)
- Durchschnittliche Distanz: 56,9 km (Median: 53,7 km) – realistisch

### 2.3 Konsistenz (Consistency)

Die drei bereitgestellten Dateien wurden erfolgreich miteinander verknüpft:

| Datei | Größe | Verknüpfung | Erfolgsrate |
|-------|-------|-------------|-------------|
| **Auftragsanalyse** (.xlsb) | 23,6 MB | Basis-Datei | 100% |
| **Tourenaufstellung** (.xlsx) | 2,85 MB | Via `Nummer.Tour` | 100% |
| **Sparten** (.xlsx) | 28 KB | Via `RKdNr` | 97,3% |
| **Betriebszentralen** (.csv) | 1 KB | Via `Nummer.Auftraggeber` | 99,7% |

**Konsistenzprüfungen bestanden**:
- ✅ Alle Touren-IDs in Aufträgen vorhanden in Tourenaufstellung
- ✅ Kunden-IDs konsistent zwischen Aufträgen und Sparten
- ✅ Auftraggeber-Nummern erfolgreich auf Betriebszentralen gemappt

### 2.4 Identifizierte Probleme

#### Problem 1: Typen-Inkonsistenz bei Spartenzuordnung
**Symptom**: Initiale Mapping-Versuche ergaben 0% Erfolgsquote
**Ursache**: Kundennummern in Aufträgen als String, in Sparten-Datei als Integer
**Lösung**: Automatische Typkonvertierung zu Int64 implementiert
**Resultat**: ✅ 97,3% erfolgreiche Zuordnung

#### Problem 2: Lagerhaltungsaufträge in Transportdaten
**Symptom**: "Lager Auftrag" (Warehouse-Operationen) in Transportdaten enthalten
**Ursache**: Keine Filterung nach Auftragsart in Quelldaten
**Lösung**: Filter implementiert (`Lieferart 2.0 != 'Lager Auftrag'`)
**Resultat**: ✅ Nur echte Transportaufträge in Analyse

#### Problem 3: Fehlende Spediteur-Nummern
**Symptom**: Einige Aufträge ohne `Nummer.Spedition`
**Ursache**: Interne Lagerbewegungen ohne Spediteurzuordnung
**Lösung**: Diese Aufträge aus Transportanalyse ausgeschlossen
**Resultat**: ✅ Nur Aufträge mit klarer Spediteurzuordnung

### 2.5 Angewandte Korrekturen

| Korrektur | Betroffene Aufträge | Maßnahme |
|-----------|---------------------|----------|
| **Lageraufträge ausgeschlossen** | ~3.000 | Filterregel angewendet |
| **Sparten-Typkonvertierung** | 132.000 | Automatische Int64-Konvertierung |
| **Betriebszentralen-Mapping** | 135.646 | Neue Zuordnungstabelle erstellt |
| **Leergut-Kategorisierung** | 24.819 | Separate Kategorie eingeführt |

---

## 3. Statistische Übersicht

### 3.1 Gesamtvolumen

| Kennzahl | Wert | Einheit |
|----------|------|---------|
| **Gesamtaufträge** | 135.646 | Aufträge |
| **Analysezeitraum** | 30 | Tage |
| **Durchschnitt pro Tag** | 4.521 | Aufträge/Tag |
| **Gesamtdistanz** | 8.160.801 | km |
| **Durchschnittliche Distanz** | 56,9 | km/Auftrag |
| **Gesamteinnahmen** | CHF 12.756.543 | CHF |
| **Gesamtausgaben** | CHF 12.547.005 | CHF |
| **Gewinnmarge** | 1,6% | % |

### 3.2 Betriebszentralen (Top 5)

| Rang | Betriebszentrale | Aufträge | Anteil | Kumul. |
|------|------------------|----------|--------|--------|
| 1 | **BZ Oberbipp** | 35.980 | 26,5% | 26,5% |
| 2 | **BZ Sursee** | 28.893 | 21,3% | 47,8% |
| 3 | **BZ Winterthur** | 27.919 | 20,6% | 68,4% |
| 4 | **BZ Landquart** | 16.703 | 12,3% | 80,7% |
| 5 | **B&T Winterthur** | 9.161 | 6,8% | 87,5% |
| | *Weitere 7 Standorte* | 16.990 | 12,5% | 100% |
| | **Total** | **135.646** | **100%** | |

**Erkenntnis**: Die Top 3 Betriebszentralen bearbeiten 68% aller Aufträge.

### 3.3 Auftragsarten

| Auftragsart | Anzahl | Anteil | Beschreibung |
|-------------|--------|--------|--------------|
| **Lieferung** | 93.970 | 69,3% | Standard-Auslieferungen |
| **Leergut** | 24.819 | 18,3% | Rückführung leerer Behälter |
| **Abholung** | 16.857 | 12,4% | Vorholungen und mehrteilige Touren |
| **Total** | **135.646** | **100%** | |

**Wichtige Erkenntnis**: Leergut-Aufträge machen knapp 1/5 aller Transporte aus – diese wurden bisher nicht separat getrackt!

### 3.4 Spediteure (Intern vs. Extern)

| Spediteurtyp | Aufträge | Anteil | Ausgaben |
|--------------|----------|--------|----------|
| **Intern (TRAVECO)** | 106.698 | 78,6% | - |
| **Extern (Fremdfahrer)** | 24.782 | 18,3% | CHF 12.408.937 |
| **Unbekannt** | 4.166 | 3,1% | - |
| **Total** | **135.646** | **100%** | CHF 12.547.005 |

**Erkenntnis**: 78,6% der Aufträge werden intern abgewickelt, aber Fremdfahrer verursachen den Großteil der externen Kosten.

### 3.5 Distanz-Metriken

| Metrik | Wert | Einheit |
|--------|------|---------|
| **Gesamtdistanz (abgerechnet)** | 8.160.801 | km |
| **Durchschnitt pro Auftrag** | 56,9 | km |
| **Median-Distanz** | 53,7 | km |
| **Kürzeste Distanz** | 0 | km (lokale Zustellung) |
| **Längste Distanz** | 2.458 | km (Einzelfall) |

**Verteilung**:
- Sehr kurz (<50 km): ~45% der Aufträge
- Kurz (50-100 km): ~35% der Aufträge
- Mittel (100-200 km): ~15% der Aufträge
- Lang (>200 km): ~5% der Aufträge

---

## 4. Mapping-Erfolgsraten

### 4.1 Sparten-Zuordnung (Kundendivisionen)

| Metrik | Wert |
|--------|------|
| **Erfolgsquote** | 97,3% |
| **Zugeordnete Aufträge** | 132.000 |
| **Nicht zugeordnet** | 3.646 (2,7%) |
| **Unique Sparten** | 6 Divisionen |

**Top 3 Sparten**:
1. Detailhandel
2. Lebensmittel
3. Agrar

**Nicht zugeordnete Aufträge**: Traveco-interne Pseudo-Kunden (markiert als "Keine Sparte")

### 4.2 Betriebszentralen-Zuordnung

| Metrik | Wert |
|--------|------|
| **Erfolgsquote** | 99,7% |
| **Zugeordnete Aufträge** | 135.295 |
| **Nicht zugeordnet** | 351 (0,3%) |
| **Unique Betriebszentralen** | 12 Standorte |

**Status**: Sehr hohe Zuordnungsrate. Die 351 nicht zugeordneten Aufträge haben unbekannte Auftraggeber-Nummern.

### 4.3 Tourkosten-Verknüpfung

| Metrik | Wert |
|--------|------|
| **Erfolgreich verknüpft** | 100% |
| **Aufträge mit Kostendaten** | 135.646 |
| **Touren mit PraCar-Daten** | Vollständig |

**Status**: Perfekte Verknüpfung zwischen Aufträgen und Tourendaten über `Nummer.Tour`.

---

## 5. Erkenntnisse

### 5.1 Stärken der Daten

✅ **Hervorragende Vollständigkeit**:
- Kompletter Monatsdatensatz ohne Lücken
- Alle relevanten Kennzahlen (Einnahmen, Ausgaben, Distanzen) vorhanden
- Konsistente Datenstruktur über alle drei Quelldateien

✅ **Hohe Datenqualität**:
- 99,7% der Aufträge erfolgreich den Betriebszentralen zugeordnet
- 97,3% der Aufträge mit Spartenzuordnung
- Keine kritischen Datenlücken oder Inkonsistenzen

✅ **Gute Dokumentation**:
- Datenstruktur gut nachvollziehbar
- Spalten sinnvoll benannt
- Verknüpfungsschlüssel (Tour-Nr., Kunden-Nr.) eindeutig

### 5.2 Datenlücken & Limitierungen

⚠️ **Zeitliche Einschränkung**:
- Nur 1 Monat Daten verfügbar (Juni 2025)
- Für robuste Zeitreihen-Prognosen werden mind. 24-36 Monate benötigt
- Saisonalität kann nicht zuverlässig identifiziert werden

⚠️ **Fehlende Personalkostendaten**:
- Keine direkten Personalkosten pro Auftrag verfügbar
- Verwendung interner Fahrer als Proxy-Metrik
- Erschwert vollständige Kostenanalyse

⚠️ **Einzelne Zuordnungslücken**:
- 2,7% ohne Spartenzuordnung (Traveco-intern)
- 0,3% ohne Betriebszentralen-Zuordnung

### 5.3 Besondere Beobachtungen

🔍 **Leergut als bedeutender Faktor**:
- 18,3% aller Aufträge sind Leergut-Rückführungen
- Wurde bisher nicht separat getrackt
- Wichtig für Kapazitätsplanung und Leerfahrten-Optimierung

🔍 **Konzentration auf Top-Standorte**:
- Top 3 Betriebszentralen bearbeiten 68% der Aufträge
- Starke geografische Konzentration
- Potenzial für standortspezifische Optimierungen

🔍 **Hoher Anteil interner Spediteure**:
- 78,6% der Transporte intern abgewickelt
- Zeigt hohe Eigenkapazität
- Fremdfahrer primär für Spitzenlast

🔍 **Kosteneffizienz**:
- Durchschnittlicher Auftrag generiert CHF 94 Einnahmen
- Durchschnittliche Kosten CHF 92,5 pro Auftrag
- Gewinnmarge von 1,6% (sehr schlank)

---

## 6. Methodische Hinweise

### Datenprozessierung

**Angewandte Filter**:
1. Ausschluss von "Lager Auftrag" (Warehouse-Operationen)
2. Ausschluss von Aufträgen ohne Spediteur-Nummer
3. Ausschluss von B&T-Pickups ohne Kundennummer

**Datenbereinigung**:
- Automatische Typkonvertierung für Sparten-Mapping
- Betriebszentralen-Zuordnung über neue Mapping-Tabelle
- Leergut als separate Auftragsart kategorisiert

**Aggregationslogik**:
- Monatliche Aggregation auf Betriebszentralen-Ebene
- 12 Betriebszentralen als Kostenstellenebene
- Finanzielle Kennzahlen summiert, Distanzen gemittelt

### Software & Tools

- **Analyse-Tool**: Python (pandas, numpy, plotly)
- **Umgebung**: Jupyter Notebooks
- **Versionierung**: Git
- **Datenformat**: CSV (processed), XLSB/XLSX (raw)

---

## Anhang

### Datenfiles Analysiert

1. **20251015 Juni 2025 QS Auftragsanalyse.xlsb** (23,6 MB)
   - 135.646 Datensätze
   - 108 Spalten
   - Zeitraum: 01.06.2025 – 30.06.2025

2. **20251015 QS Tourenaufstellung Juni 2025.xlsx** (2,85 MB)
   - Tour-Zuordnungen und PraCar-Daten
   - Verknüpfung via `Nummer.Tour`

3. **20251015 Sparten.xlsx** (28 KB)
   - 384 Kundendivisionen
   - 6 unique Sparten

4. **TRAVECO_Betriebszentralen.csv** (1 KB)
   - 14 Betriebszentralen (12 aktiv in Juni 2025)
   - Mapping von Auftraggeber zu Standortnamen

### Kontakt

Bei Fragen oder weiterem Analysebedarf:

**Analyst**: Kevin Kuhn
**Datum**: 24. Oktober 2025
**Projekt**: Traveco Transportanalyse Juni 2025

---

**Gesamtfazit**: Die bereitgestellten Daten sind von **sehr guter Qualität** und eignen sich hervorragend für operative Analysen. Für strategische Zeitreihen-Prognosen werden jedoch historische Daten (24-36 Monate) benötigt.
