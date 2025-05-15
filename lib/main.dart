import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(KortingAIApp());

class KortingAIApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KortingFinder AI',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();
  String? _antwoord;
  bool _loading = false;

  Future<String> fetchKortingViaAI(String bedrijf) async {
    final apiKey = const String.fromEnvironment('OPENAI_API_KEY');
    const endpoint = 'https://api.openai.com/v1/chat/completions';

    final response = await http.post(
      Uri.parse(endpoint),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
      },
      body: jsonEncode({
        'model': 'gpt-3.5-turbo',
        'messages': [
          {
            'role': 'system',
            'content':
            'Je bent een slimme assistent die mensen helpt bij het vinden van actuele kortingscodes voor webshops. '
                'Geef duidelijke en bruikbare suggesties op basis van wat recent of vaak gebruikt wordt. '
                'Als je niet zeker bent, geef dan voorbeelden van populaire of mogelijk werkende codes. '
                'Gebruik alleen tekst, en geef geen disclaimers tenzij noodzakelijk.'
          },
          {
            'role': 'user',
            'content':
            'Wat zijn mogelijke actuele kortingscodes of aanbiedingen voor $bedrijf?'
          }
        ],
        'temperature': 1.0,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['choices'][0]['message']['content'].toString().trim();
    } else {
      return 'Fout van AI: ${response.statusCode} - ${response.body}';
    }
  }

  void _zoekKorting() async {
    final winkel = _controller.text.trim();
    if (winkel.isEmpty) return;

    setState(() {
      _antwoord = null;
      _loading = true;
    });

    final resultaat = await fetchKortingViaAI(winkel);

    setState(() {
      _antwoord = resultaat;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('KortingFinder AI')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Voer een winkelnaam in (bijv. zalando)',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => _zoekKorting(),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _zoekKorting,
              child: Text('Zoek korting'),
            ),
            SizedBox(height: 30),
            if (_loading) CircularProgressIndicator(),
            if (_antwoord != null) ...[
              Text(
                'Antwoord van AI:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 10),
              Text(_antwoord!),
            ],
          ],
        ),
      ),
    );
  }
}
