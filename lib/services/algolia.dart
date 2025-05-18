import 'package:algolia/algolia.dart';

class AlgoliaService {
  static const Algolia _algolia = Algolia.init(
    applicationId: 'E51E1ZIN4O', // Vervang met jouw echte Application ID
    apiKey: '9d15da91ccac3f3e3c7ec0710061dd1d',   // Vervang met jouw Algolia **Search-Only API Key**
  );

  Future<List<AlgoliaObjectSnapshot>> searchInfluencers(String query) async {
    final results = await _algolia.instance
        .index('influencers') // Dit moet overeenkomen met jouw indexnaam
        .query(query)
        .getObjects();

    return results.hits;
  }
}
