import {NextResponse} from "next/server";
import {buildReleaseGateSnapshot} from "@/server/operable-release-gate";
import {buildReleaseGateViewModel} from "@/lib/operable-release-gate/release-gate-view-model";
export async function GET(){const snapshot=buildReleaseGateSnapshot();return NextResponse.json({ok:true,data:buildReleaseGateViewModel(snapshot),meta:{package:snapshot.packageName}})}
