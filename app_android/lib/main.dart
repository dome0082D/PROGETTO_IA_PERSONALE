import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(const MioAssistenteIA());

class MioAssistenteIA extends StatelessWidget {
  const MioAssistenteIA({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'IA Personale - Agente Android',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F0F0F),
        primaryColor: const Color(0xFF00FF66),
      ),
      home: const SchermataAgente(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SchermataAgente extends StatefulWidget {
  const SchermataAgente({super.key});

  @override
  State<SchermataAgente> createState() => _SchermataAgenteState();
}

class _SchermataAgenteState extends State<SchermataAgente>
    with SingleTickerProviderStateMixin {
  final TextEditingController _controllerTesto = TextEditingController();
  late WebSocketChannel _canaleWebSocket;
  
  // Controller per l'animazione dell'equalizzatore grafico
  late AnimationController _equalizzatoreController;
  
  String _statoConnessione = "Disconnesso";
  String _utimoMessaggioIA = "In attesa di input...";
  bool _iaStaParlando = false;

  // INSERISCI QUI L'IP DEL TUO PC (es. ws://192.168.1.50:8000/ws/android)
  // Per i test in locale sul PC attuale o su emulatore puoi usare localhost/10.0.2.2
  final String _urlServer = "ws://10.0.2.2:8000/ws/android";

  @override
  void initState() {
    super.initState();
    _equalizzatoreController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    )..repeat(reverse: true);

    _connettiAlCervello();
  }

  void _connettiAlCervello() {
    try {
      _canaleWebSocket = WebSocketChannel.connect(Uri.parse(_urlServer));
      setState(() => _statoConnessione = "Connesso al Cervello Centrale");

      // Ascolto perenne in background dei pacchetti inviati da Python
      _canaleWebSocket.stream.listen(
        (pacchettoRicevuto) {
          final dati = jsonDecode(pacchettoRicevuto);
          
          if (dati['azione'] == 'SPEAK_AND_ANIMATE') {
            setState(() {
              _utimoMessaggioIA = dati['parametri']['testo'];
              _iaStaParlando = true;
            });
            // Ferma l'animazione dopo 4 secondi (o al termine del parlato vocale)
            Future.delayed(const Duration(seconds: 4), () {
              if (mounted) setState(() => _iaStaParlando = false);
            });
          }
        },
        onError: (error) => setState(() => _statoConnessione = "Errore di connessione"),
        onDone: () => setState(() => _statoConnessione = "Disconnesso"),
      );
    } catch (e) {
      setState(() => _statoConnessione = "Impossibile raggiungere il server");
    }
  }

  void _inviaMessaggio() {
    if (_controllerTesto.text.isEmpty) return;

    // Struttura JSON rigorosa che rispetta il modello Pydantic di Python
    final pacchetto = {
      "mittente": "android",
      "tipo": "testo",
      "contenuto": _controllerTesto.text,
      "dati_extra": {}
    };

    _canaleWebSocket.sink.add(jsonEncode(pacchetto));
    _controllerTesto.clear();
  }

  @override
  void dispose() {
    _canaleWebSocket.sink.close();
    _equalizzatoreController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_statoConnessione, style: const TextStyle(fontSize: 14)),
        backgroundColor: Colors.black,
        elevation: 0,
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // --- SEZIONE DISPLAY CON RIGA VIBRANTE (EQUALIZZATORE) ---
          Expanded(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // L'equalizzatore compare e vibra quando l'IA elabora o risponde
                  if (_iaStaParlando)
                    AnimatedBuilder