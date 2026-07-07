import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'IA Personale Totale',
      theme: ThemeData(brightness: Brightness.dark, useMaterial3: true),
      home: const MonitorPage(),
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});

  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  late WebSocketChannel channel;

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Sistema IA Totale Online")),
      body: Center(
        child: StreamBuilder(
          stream: channel.stream,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              final Map<String, dynamic> dati = jsonDecode(snapshot.data);
              final monitoraggio = dati['monitoraggio'];
              final statoSicurezza = dati['sicurezza']; // NORMALE o ALTA_ATTENZIONE

              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // --- LA RIGA VIVA (Equalizzatore/Respiro) ---
                  Container(
                    height: 10,
                    width: (monitoraggio['cpu'] * 3).toDouble(),
                    decoration: BoxDecoration(
                      color: statoSicurezza == "NORMALE" ? Colors.blueAccent : Colors.redAccent,
                      boxShadow: [BoxShadow(color: Colors.blue.withOpacity(0.5), blurRadius: 10)],
                    ),
                  ),
                  const SizedBox(height: 40),
                  
                  Text("STATO: $statoSicurezza", 
                    style: TextStyle(color: statoSicurezza == "NORMALE" ? Colors.green : Colors.red, fontSize: 22)),
                  
                  const SizedBox(height: 20),
                  
                  Text("${monitoraggio['cpu'].toStringAsFixed(1)}%", 
                    style: const TextStyle(fontSize: 80, fontWeight: FontWeight.bold)),
                  
                  const Text("CARICO SISTEMA", style: TextStyle(color: Colors.grey)),
                ],
              );
            }
            return const CircularProgressIndicator();
          },
        ),
      ),
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }
}