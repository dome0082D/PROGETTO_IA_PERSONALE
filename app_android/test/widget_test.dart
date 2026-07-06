import 'package:flutter_test/flutter_test.dart';
import 'package:tuo_nome_progetto/main.dart'; // Sostituisci 'tuo_nome_progetto' con il nome reale della tua cartella

void main() {
  testWidgets('Test avvio app', (WidgetTester tester) async {
    // Carica l'app
    await tester.pumpWidget(const AppPersonale());

    // Verifica che il testo sia presente
    expect(find.text('Monitoraggio IA attivo'), findsOneWidget);
  });
}