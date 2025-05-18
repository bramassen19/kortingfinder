import 'package:flutter/material.dart';
import '../services/algolia_service.dart';

class SearchPage extends StatefulWidget {
  @override
  _SearchPageState createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final AlgoliaService _algoliaService = AlgoliaService();
  List _results = [];
  String _query = '';

  void _search() async {
    final hits = await _algoliaService.searchInfluencers(_query);
    setState(() {
      _results = hits;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Zoek Kortingscodes')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              decoration: InputDecoration(
                hintText: 'Zoek op influencer of bedrijf...',
                suffixIcon: IconButton(
                  icon: Icon(Icons.search),
                  onPressed: _search,
                ),
              ),
              onChanged: (val) => _query = val,
              onSubmitted: (_) => _search(),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _results.length,
                itemBuilder: (context, index) {
                  final item = _results[index].data;
                  return ListTile(
                    title: Text(item['naam'] ?? 'Onbekend'),
                    subtitle: Text("Code: ${item['code']}"),
                    trailing: Text(item['bedrijf'] ?? ''),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
