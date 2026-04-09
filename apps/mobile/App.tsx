import { StatusBar } from "expo-status-bar";
import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

type ScheduledEvent = {
  title: string;
  start: string;
  end: string;
};

type ChatResponse = {
  session_id: string;
  reply: string;
  changes: {
    mode: string;
    events: ScheduledEvent[];
    warnings: string[];
  };
};

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  events?: ScheduledEvent[];
  warnings?: string[];
};

const API_BASE_URL = process.env.EXPO_PUBLIC_DAYLI_API_URL ?? "http://127.0.0.1:8000";

const starterPrompts = [
  "Plan work from 9-12, gym at 6, dinner at 8",
  "Move my gym to tomorrow",
  "Make my morning less busy",
];

export default function App(): React.JSX.Element {
  const [sessionId] = useState(() => `ios-demo-${Date.now()}`);
  const [userId] = useState("iphone-demo");
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Describe your day and I’ll turn it into a calendar preview you can refine.",
    },
  ]);

  const canSend = useMemo(() => input.trim().length > 0 && !isLoading, [input, isLoading]);

  async function submitMessage(message: string): Promise<void> {
    const trimmed = message.trim();
    if (!trimmed) {
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message: trimmed,
          mode: "preview",
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`);
      }

      const data = (await response.json()) as ChatResponse;
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: data.reply,
          events: data.changes.events,
          warnings: data.changes.warnings,
        },
      ]);
    } catch (error) {
      const messageText =
        error instanceof Error
          ? `${error.message}. Update EXPO_PUBLIC_DAYLI_API_URL if your backend is running on another host.`
          : "Something went wrong while calling the Dayli API.";
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          text: messageText,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.header}>
          <Text style={styles.eyebrow}>Dayli</Text>
          <Text style={styles.title}>Conversational calendar planning for your iPhone demo</Text>
          <Text style={styles.subtitle}>
            Start with a natural-language plan, then refine it by chatting.
          </Text>
        </View>

        <ScrollView contentContainerStyle={styles.messageList}>
          {messages.map((message) => (
            <View
              key={message.id}
              style={[
                styles.messageBubble,
                message.role === "user" ? styles.userBubble : styles.assistantBubble,
              ]}
            >
              <Text style={styles.messageRole}>
                {message.role === "user" ? "You" : "Dayli"}
              </Text>
              <Text
                style={[
                  styles.messageText,
                  message.role === "user" ? styles.userMessageText : styles.assistantMessageText,
                ]}
              >
                {message.text}
              </Text>
              {message.events?.length ? (
                <View style={styles.cardStack}>
                  {message.events.map((event) => (
                    <View key={`${message.id}-${event.title}-${event.start}`} style={styles.eventCard}>
                      <Text style={styles.eventTitle}>{event.title}</Text>
                      <Text style={styles.eventTime}>{formatEventWindow(event)}</Text>
                    </View>
                  ))}
                </View>
              ) : null}
              {message.warnings?.length ? (
                <View style={styles.warningBox}>
                  {message.warnings.map((warning) => (
                    <Text key={`${message.id}-${warning}`} style={styles.warningText}>
                      {warning}
                    </Text>
                  ))}
                </View>
              ) : null}
            </View>
          ))}

          {isLoading ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator color="#1D6E5B" />
              <Text style={styles.loadingText}>Dayli is planning your schedule...</Text>
            </View>
          ) : null}
        </ScrollView>

        <View style={styles.promptRow}>
          {starterPrompts.map((prompt) => (
            <Pressable key={prompt} style={styles.promptChip} onPress={() => submitMessage(prompt)}>
              <Text style={styles.promptChipText}>{prompt}</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.composer}>
          <TextInput
            style={styles.input}
            placeholder="Tell Dayli about your day..."
            placeholderTextColor="#66756E"
            value={input}
            onChangeText={setInput}
            multiline
          />
          <Pressable
            style={[styles.sendButton, !canSend && styles.sendButtonDisabled]}
            disabled={!canSend}
            onPress={() => submitMessage(input)}
          >
            <Text style={styles.sendButtonText}>Send</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function formatEventWindow(event: ScheduledEvent): string {
  const start = new Date(event.start);
  const end = new Date(event.end);
  return `${start.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  })} • ${start.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })} - ${end.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  })}`;
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#F4EFE6",
  },
  container: {
    flex: 1,
    paddingHorizontal: 18,
    paddingBottom: 16,
  },
  header: {
    paddingTop: 18,
    paddingBottom: 16,
  },
  eyebrow: {
    color: "#1D6E5B",
    fontSize: 14,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  title: {
    marginTop: 8,
    color: "#18211E",
    fontSize: 30,
    fontWeight: "800",
    lineHeight: 36,
  },
  subtitle: {
    marginTop: 8,
    color: "#4C5D56",
    fontSize: 15,
    lineHeight: 22,
  },
  messageList: {
    gap: 12,
    paddingBottom: 16,
  },
  messageBubble: {
    borderRadius: 24,
    padding: 16,
  },
  userBubble: {
    backgroundColor: "#18211E",
  },
  assistantBubble: {
    backgroundColor: "#FFFDF8",
    borderWidth: 1,
    borderColor: "#D9D2C7",
  },
  messageRole: {
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.8,
    color: "#809087",
    marginBottom: 8,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 23,
  },
  userMessageText: {
    color: "#F9F8F4",
  },
  assistantMessageText: {
    color: "#18211E",
  },
  cardStack: {
    gap: 10,
    marginTop: 14,
  },
  eventCard: {
    backgroundColor: "#E5F1ED",
    borderRadius: 18,
    padding: 14,
  },
  eventTitle: {
    color: "#123A30",
    fontSize: 16,
    fontWeight: "700",
  },
  eventTime: {
    marginTop: 4,
    color: "#31574C",
    fontSize: 14,
  },
  warningBox: {
    marginTop: 12,
    backgroundColor: "#FFF1D6",
    borderRadius: 14,
    padding: 12,
  },
  warningText: {
    color: "#7A5A14",
    fontSize: 13,
    lineHeight: 18,
  },
  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingVertical: 10,
  },
  loadingText: {
    color: "#4C5D56",
    fontSize: 14,
  },
  promptRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  promptChip: {
    backgroundColor: "#E9E0D2",
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  promptChipText: {
    color: "#3D4034",
    fontSize: 13,
    fontWeight: "600",
  },
  composer: {
    backgroundColor: "#FFFDF8",
    borderRadius: 24,
    padding: 10,
    borderWidth: 1,
    borderColor: "#D9D2C7",
  },
  input: {
    minHeight: 68,
    maxHeight: 130,
    color: "#18211E",
    fontSize: 16,
    lineHeight: 22,
    paddingHorizontal: 8,
    paddingTop: 8,
  },
  sendButton: {
    alignSelf: "flex-end",
    marginTop: 8,
    backgroundColor: "#1D6E5B",
    borderRadius: 999,
    paddingHorizontal: 18,
    paddingVertical: 12,
  },
  sendButtonDisabled: {
    backgroundColor: "#95B0A7",
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
});
