import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class KortingscodeZoeker extends StatefulWidget {
  @override
  _KortingscodeZoekerState createState() => _KortingscodeZoekerState();
}

class _KortingscodeZoekerState extends State<KortingscodeZoeker> {
  final TextEditingController _controller = TextEditingController();

  Future<List<Map<String, dynamic>>> fetchKortingscodes(String winkel) async {
    final url = Uri.parse("https://kortingfinder.web.app/kortingscodes.json");
    final resp = await http.get(url);
    if (resp.statusCode != 200) {
      throw Exception("Kon data niet laden (${resp.statusCode})");
    }
    final data = jsonDecode(resp.body);
    final List all = data["kortingscodes"];
    // Filter op bedrijf (case-insensitive)
    return all
        .where((item) =>
            (item["bedrijf"] as String).toLowerCase() ==
            winkel.toLowerCase())
        .cast<Map<String, dynamic>>()
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('KortingFinder'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Voer een winkelnaam in (bijv. zalando)',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => setState(() {}),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => setState(() {}),
              child: Text('Zoek korting'),
            ),
            const SizedBox(height: 24),
            Expanded(
              child: FutureBuilder<List<Map<String, dynamic>>>(
                future: fetchKortingscodes(_controller.text.trim()),
                builder: (ctx, snap) {
                  if (_controller.text.trim().isEmpty) {
                    return Center(child: Text('Typ een winkelnaam om te zoeken.'));
                  }
                  if (snap.connectionState == ConnectionState.waiting) {
                    return Center(child: CircularProgressIndicator());
                  }
                  if (snap.hasError) {
                    return Center(child: Text('Fout: ${snap.error}'));
                  }
                  final codes = snap.data!;
                  if (codes.isEmpty) {
                    return Center(
                      child: Text(
                        'Er zijn momenteel geen werkende kortingscodes voor '
                        '${_controller.text.trim()}.\nWe blijven actief zoeken!',
                        textAlign: TextAlign.center,
                      ),
                    );
                  }
                  return ListView.separated(
                    itemCount: codes.length,
                    separatorBuilder: (_, __) => Divider(),
                    itemBuilder: (_, i) {
                      final c = codes[i];
                      if (c.containsKey('bericht')) {
                        return Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(
                            c['bericht'],
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontStyle: FontStyle.italic,
                              color: Colors.grey[700],
                            ),
                          ),
                        );
                      }
                      return ListTile(
                        title: Text(c['code'] ?? ''),
                        subtitle: c['geldig_tot'] != null && c['geldig_tot'] != ''
                            ? Text('Geldig tot ${c['geldig_tot']}')
                            : null,
                        trailing: IconButton(
                          icon: Icon(Icons.copy),
                          onPressed: () {
                            Clipboard.setData(ClipboardData(text: c['code']));
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Code gekopieerd!')),
                            );
                          },
                        ),
                      );
                    },
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}
