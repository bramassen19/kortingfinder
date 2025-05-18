const functions = require("firebase-functions");
const admin = require("firebase-admin");
const algoliasearch = require("algoliasearch").default; // ✅ Correct

admin.initializeApp();

// 🔑 Algolia configuratie
const ALGOLIA_APP_ID = "E51E1ZIN4O";
const ALGOLIA_ADMIN_KEY = "e53d1e5f02309615b38555bbb83e7a61";
const ALGOLIA_INDEX_NAME = "influencers";

const algoliaClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_ADMIN_KEY);
const index = algoliaClient.initIndex(ALGOLIA_INDEX_NAME);

// 🔁 Sync Firestore -> Algolia
exports.syncInfluencerToAlgolia = functions.firestore
  .document("influencers/{influencerId}")
  .onWrite((change, context) => {
    const doc = change.after.exists ? change.after.data() : null;
    const objectID = context.params.influencerId;

    if (doc) {
      console.log("Toevoegen aan Algolia:", { ...doc, objectID });
      return index.saveObject({ ...doc, objectID });
    } else {
      console.log("Verwijderen uit Algolia:", objectID);
      return index.deleteObject(objectID);
    }
  });
