import 'package:flutter/material.dart';

void main() {
  runApp(const AppPersonale());
}

class AppPersonale extends StatelessWidget {
  const AppPersonale({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Qui va il tuo widget o logica
              const Text("Monitoraggio IA attivo"),
            ],
          ),
        ),
      ),
    );
  }
}