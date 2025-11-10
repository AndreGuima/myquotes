import React, { useEffect, useState } from 'react';
import { FlatList, ActivityIndicator, StyleSheet } from 'react-native';
import { ThemedView } from "@/components/themed-view";
import { ThemedText } from "@/components/themed-text";
import api from "@/app/services/api";

export default function QuotesScreen() {
  const [quotes, setQuotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQuotes = async () => {
    try {
      const response = await api.get('/quotes');
      setQuotes(response.data);
    } catch (error) {
      console.error('Error fetching quotes:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotes();
  }, []);

  if (loading) {
    return (
      <ThemedView style={styles.center}>
        <ActivityIndicator size="large" />
        <ThemedText>Loading quotes...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <FlatList
        data={quotes}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <ThemedView style={styles.quoteItem}>
            <ThemedText style={styles.quoteText}>“{item.text}”</ThemedText>
            <ThemedText style={styles.quoteAuthor}>— {item.author}</ThemedText>
          </ThemedView>
        )}
        ListEmptyComponent={<ThemedText>No quotes found.</ThemedText>}
      />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  quoteItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#555',
    marginBottom: 8,
  },
  quoteText: { fontSize: 16, fontStyle: 'italic' },
  quoteAuthor: { fontSize: 14, marginTop: 4, opacity: 0.7 },
});
