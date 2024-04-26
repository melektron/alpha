/*
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
25.04.23, 09:38

Zod message definitions for the kayeet game
*/

import { z } from "zod";

export const login_message = z.object({
    type: z.literal("login"),
    username: z.string(),
});
export type LoginMessage = z.infer<typeof login_message>;

export const login_confirm_message = z.object({
    type: z.literal("confirm"),
});
export type LoginConfirmMessage = z.infer<typeof login_confirm_message>;

export enum ErrorCode {
    InvalidLogin = 0,
    NotLoggeInYet = 1,
    InvalidRequest = 2,
    InvalidMessage = 3,
    QuestionTimeout = 4
}

export const error_message = z.object({
    type: z.literal("error"),
    error_type: z.nativeEnum(ErrorCode),
    cause: z.string().optional(),
});
export type ErrorMessage = z.infer<typeof error_message>;

export enum QuestionType {
    TextQuestion = 0,
    YesNoQuestion = 1,
    MultiQuestion = 2
}

export const text_question_message = z.object({
    type: z.literal("question"),
    question_type: z.literal(QuestionType.TextQuestion),
    id: z.number(),
    question: z.string(),
});
export type TextQuestionMessage = z.infer<typeof text_question_message>;

export const yes_no_question_message = z.object({
    type: z.literal("question"),
    question_type: z.literal(QuestionType.YesNoQuestion),
    id: z.number(),
    question: z.string(),
});
export type YesNoQuestionMessage = z.infer<typeof text_question_message>;

export const multi_question_message = z.object({
    type: z.literal("question"),
    question_type: z.literal(QuestionType.MultiQuestion),
    id: z.number(),
    question: z.string(),
    choices: z.array(z.string()),
});
export type MultiQuestionMessage = z.infer<typeof text_question_message>;

export const question_message = z.discriminatedUnion("question_type", [
    text_question_message,
    yes_no_question_message,
    multi_question_message,
]);
export type QuestionMessage = z.infer<typeof question_message>;

// cannot nest discriminated unions yet
export const any_question_message = z.object({
    type: z.literal("question"),
    question_type: z.number(),
    id: z.number(),
    question: z.string(),
    choices: z.array(z.string()).optional()
});
export type AnyQuestionMessage = z.infer<typeof any_question_message>;

export const incoming_message = z.discriminatedUnion("type", [
    login_confirm_message,
    error_message,
    any_question_message,
]);
export type IncomingMessage = z.infer<typeof incoming_message>;

