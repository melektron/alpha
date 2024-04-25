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

export const kayeet_message = z.discriminatedUnion("type", [
    login_message,
    login_confirm_message,
    error_message
]);
export type KayeetMessage = z.infer<typeof kayeet_message>;

