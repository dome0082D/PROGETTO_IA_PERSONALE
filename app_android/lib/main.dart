import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true),
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
    // Connessione al server locale (Python)
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
  }

  void inviaComando(String azione) {
    channel.sink.add(json.encode({"azione": azione}));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (snapshot.hasError) return Center(child: Text("Errore: ${snapshot.error}"));
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          
          // Gestione sicura dei dati
          final mon = dati['monitoraggio'] ?? {'cpu': 0.0};
          final domanda = dati['domanda'] ?? "";

          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("SICUREZZA: ${dati['sicurezza']}", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                const SizedBox(height: 20),
                Text("${mon['cpu'].toStringAsFixed(1)}% CPU", style: const TextStyle(fontSize: 40)),
                const SizedBox(height: 30),
                
                // Se c'è una domanda, mostriamo i pulsanti
                if (domanda != "Sistema ok." && domanda != "")
                  Column(
                    children: [
                      Text(domanda, style: const TextStyle(color: Colors.yellow, fontSize: 18)),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          ElevatedButton(onPressed: () => inviaComando("pulisci"), child: const Text("SI")),
                          const SizedBox(width: 20),
                          ElevatedButton(onPressed: () => print("Annullato"), child: const Text("NO")),
                        ],
                      ),
                    ],
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }
}